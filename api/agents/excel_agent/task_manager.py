from typing import AsyncIterable
from common.types import (
    SendTaskRequest,
    TaskSendParams,
    Message,
    TaskStatus,
    Artifact,
    TextPart,
    FilePart,
    FileContent,
    TaskState,
    SendTaskResponse,
    InternalError,
    JSONRPCResponse,
    SendTaskStreamingRequest,
    SendTaskStreamingResponse,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
    Task,
    TaskIdParams,
    PushNotificationConfig,
    InvalidParamsError,
)
from common.server.task_manager import InMemoryTaskManager
from excel_agent.agent import ExcelAgent
from core.models import ExcelRequestMessage
from common.utils.push_notification_auth import PushNotificationSenderAuth
import common.server.utils as utils
from typing import Union, Dict, Any, List
import asyncio
import logging
import traceback
import base64
import os
import json
import mimetypes

logger = logging.getLogger(__name__)


class ExcelAgentTaskManager(InMemoryTaskManager):
    def __init__(self, agent: ExcelAgent, notification_sender_auth: PushNotificationSenderAuth):
        super().__init__()
        self.agent = agent
        self.notification_sender_auth = notification_sender_auth

    def _validate_request(
        self, request: Union[SendTaskRequest, SendTaskStreamingRequest]
    ) -> JSONRPCResponse | None:
        task_send_params: TaskSendParams = request.params
        if not utils.are_modalities_compatible(
            task_send_params.acceptedOutputModes, ExcelAgent.SUPPORTED_CONTENT_TYPES
        ):
            logger.warning(
                "Unsupported output mode. Received %s, Support %s",
                task_send_params.acceptedOutputModes,
                ExcelAgent.SUPPORTED_CONTENT_TYPES,
            )
            return utils.new_incompatible_types_error(request.id)
        
        if task_send_params.pushNotification and not task_send_params.pushNotification.url:
            logger.warning("Push notification URL is missing")
            return JSONRPCResponse(id=request.id, error=InvalidParamsError(message="Push notification URL is missing"))
        
        return None

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """Handles the 'send task' request."""
        validation_error = self._validate_request(request)
        if validation_error:
            return SendTaskResponse(id=request.id, error=validation_error.error)
        
        if request.params.pushNotification:
            if not await self.set_push_notification_info(request.params.id, request.params.pushNotification):
                return SendTaskResponse(id=request.id, error=InvalidParamsError(message="Push notification URL is invalid"))

        await self.upsert_task(request.params)
        task = await self.update_store(
            request.params.id, TaskStatus(state=TaskState.WORKING), None
        )
        await self.send_task_notification(task)

        task_send_params: TaskSendParams = request.params
        excel_request = self._parse_excel_request(task_send_params)
        
        try:
            agent_response = self.agent.process_request(excel_request)
            return await self._process_agent_response(
                request, agent_response, excel_request
            )
        except Exception as e:
            logger.error(f"Error processing Excel request: {e}")
            logger.error(traceback.format_exc())
            return SendTaskResponse(
                id=request.id,
                error=InternalError(message=f"Failed to generate Excel file: {str(e)}")
            )

    async def _process_agent_response(
        self, request: SendTaskRequest, agent_response: Dict[str, Any],
        excel_request: ExcelRequestMessage
    ) -> SendTaskResponse:
        """Processes the agent's response and updates the task store."""
        task_send_params: TaskSendParams = request.params
        task_id = task_send_params.id
        history_length = task_send_params.historyLength
        
        # Create response message
        message_text = f"Excel file generated successfully from {len(excel_request.result)} records."
        message = Message(
            role="agent", 
            parts=[{"type": "text", "text": message_text}]
        )
        
        # Extract file path from response
        file_path = agent_response["content"]["file_path"]
        file_name = agent_response["content"]["file_name"]
        
        # Create artifact with file part
        artifact = self._create_file_artifact(file_path, file_name)
        
        # Update task status
        task_status = TaskStatus(state=TaskState.COMPLETED, message=message)
        task = await self.update_store(task_id, task_status, [artifact])
        task_result = self.append_task_history(task, history_length)
        await self.send_task_notification(task)
        
        return SendTaskResponse(id=request.id, result=task_result)
    
    def _parse_excel_request(self, task_send_params: TaskSendParams) -> ExcelRequestMessage:
        """Extract SQL result data from the message parts"""
        # Initialize with default values
        query = ""
        sql_query = ""
        result_data = []
        format_options = {}
        
        # Parse message parts
        for part in task_send_params.message.parts:
            if getattr(part, "type", None) == "text":
                # Try to parse the text as JSON
                try:
                    data = json.loads(part.text)
                    if isinstance(data, dict):
                        query = data.get("query", query)
                        sql_query = data.get("sql_query", sql_query)
                        result_data = data.get("result", result_data)
                        format_options = data.get("format_options", format_options)
                except json.JSONDecodeError:
                    # If not JSON, treat as the query text
                    query = part.text
            elif getattr(part, "type", None) == "data":
                data = part.data
                query = data.get("query", query)
                sql_query = data.get("sql_query", sql_query)
                result_data = data.get("result", result_data)
                format_options = data.get("format_options", format_options)
        
        return ExcelRequestMessage(
            query=query,
            sql_query=sql_query,
            result=result_data,
            format_options=format_options
        )
    
    def _create_file_artifact(self, file_path: str, file_name: str) -> Artifact:
        """Create an artifact containing the Excel file"""
        # Read the file
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        
        # Encode to base64
        encoded_bytes = base64.b64encode(file_bytes).decode("utf-8")
        
        # Determine MIME type
        mime_type = mimetypes.guess_type(file_path)[0] or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        # Create file content
        file_content = FileContent(
            name=file_name,
            mimeType=mime_type,
            bytes=encoded_bytes
        )
        
        # Create file part
        file_part = FilePart(
            type="file",
            file=file_content,
            metadata={
                "type": "excel",
                "filename": file_name,
                "size": os.path.getsize(file_path)
            }
        )
        
        # Text part explaining the file
        text_part = TextPart(
            type="text",
            text=f"Query results exported to Excel file: {file_name}"
        )
        
        # Create artifact
        return Artifact(
            name="Excel Export",
            description="SQL query results exported to Excel format",
            parts=[text_part, file_part],
            metadata={
                "rows": len(file_bytes),
                "file_size": os.path.getsize(file_path),
                "file_name": file_name
            }
        )
    
    async def send_task_notification(self, task: Task):
        """Send push notification if configured"""
        if not await self.has_push_notification_info(task.id):
            logger.info(f"No push notification info found for task {task.id}")
            return
        push_info = await self.get_push_notification_info(task.id)

        logger.info(f"Notifying for task {task.id} => {task.status.state}")
        await self.notification_sender_auth.send_push_notification(
            push_info.url,
            data=task.model_dump(exclude_none=True)
        )

    async def set_push_notification_info(self, task_id: str, push_notification_config: PushNotificationConfig):
        """Set push notification configuration with verification"""
        # Verify the ownership of notification URL by issuing a challenge request.
        is_verified = await self.notification_sender_auth.verify_push_notification_url(push_notification_config.url)
        if not is_verified:
            return False
        
        await super().set_push_notification_info(task_id, push_notification_config)
        return True 