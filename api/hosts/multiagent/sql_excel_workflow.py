import asyncio
import json
import uuid
import os
import logging
from typing import Dict, Any, List, Optional

from common.client import A2AClient, A2ACardResolver
from common.types import (
    TaskSendParams,
    Message,
    TextPart,
    DataPart,
    TaskState,
    Task,
    PushNotificationConfig
)
from core.models import SQLResultMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLExcelWorkflow:
    """
    A workflow that connects SQL Agent with Excel Agent
    
    1. Sends natural language query to SQL Agent
    2. Receives SQL query result
    3. Forwards result to Excel Agent
    4. Returns Excel file to user
    """
    
    def __init__(self, sql_agent_url: str, excel_agent_url: str, output_dir: str = None):
        """
        Initialize the workflow with agent URLs
        
        Args:
            sql_agent_url: URL of the SQL Agent
            excel_agent_url: URL of the Excel Agent
            output_dir: Directory to save output files
        """
        self.sql_agent_url = sql_agent_url
        self.excel_agent_url = excel_agent_url
        self.output_dir = output_dir or os.path.join(os.getcwd(), "outputs", "workflows")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize clients
        self.sql_card_resolver = A2ACardResolver(sql_agent_url)
        self.excel_card_resolver = A2ACardResolver(excel_agent_url)
        
        self.sql_client = A2AClient(self.sql_card_resolver.get_agent_card())
        self.excel_client = A2AClient(self.excel_card_resolver.get_agent_card())
        
        logger.info(f"Initialized SQL-Excel workflow with SQL agent at {sql_agent_url} and Excel agent at {excel_agent_url}")
    
    async def process_query(self, query: str, format_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a natural language query through the workflow
        
        Args:
            query: Natural language query for SQL database
            format_options: Optional formatting options for Excel output
            
        Returns:
            Dictionary with results including file paths
        """
        # Step 1: Create a unique session ID for this workflow run
        session_id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        
        logger.info(f"Starting workflow session {session_id} with query: {query}")
        
        # Step 2: Send query to SQL Agent
        sql_result = await self._send_to_sql_agent(query, session_id, task_id)
        
        if not sql_result or "status" not in sql_result or sql_result["status"] != "completed":
            logger.error(f"SQL Agent failed to process query: {sql_result}")
            return {
                "success": False,
                "error": "SQL Agent failed to process query",
                "details": sql_result
            }
        
        # Step 3: Extract SQL result data
        sql_data = self._extract_sql_result(sql_result)
        
        if not sql_data or "result" not in sql_data:
            logger.error(f"Failed to extract SQL result data: {sql_data}")
            return {
                "success": False,
                "error": "Failed to extract SQL result data",
                "sql_result": sql_result
            }
        
        # Step 4: Send to Excel Agent
        excel_result = await self._send_to_excel_agent(
            sql_data["query"],
            sql_data["sql_query"],
            sql_data["result"],
            format_options,
            session_id
        )
        
        if not excel_result or "status" not in excel_result or excel_result["status"] != "completed":
            logger.error(f"Excel Agent failed to process data: {excel_result}")
            return {
                "success": False,
                "error": "Excel Agent failed to process data",
                "sql_data": sql_data,
                "excel_result": excel_result
            }
        
        # Step 5: Extract file information from Excel result
        excel_file_info = self._extract_excel_file_info(excel_result)
        
        # Step 6: Combine results
        return {
            "success": True,
            "query": query,
            "sql_data": sql_data,
            "excel_file": excel_file_info
        }
    
    async def _send_to_sql_agent(self, query: str, session_id: str, task_id: str) -> Dict[str, Any]:
        """Send query to SQL Agent and get results"""
        logger.info(f"Sending query to SQL Agent: {query}")
        
        message = Message(
            role="user",
            parts=[TextPart(text=query)]
        )
        
        task_params = TaskSendParams(
            id=task_id,
            sessionId=session_id,
            message=message,
            acceptedOutputModes=["text", "data"]
        )
        
        try:
            task = await self.sql_client.send_task(task_params)
            logger.info(f"SQL Agent task completed with status: {task.status.state}")
            
            return {
                "status": task.status.state,
                "task": task
            }
        except Exception as e:
            logger.error(f"Error sending task to SQL Agent: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _extract_sql_result(self, sql_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract query result from SQL Agent response"""
        task = sql_result.get("task")
        if not task or not task.artifacts or not task.artifacts[0].parts:
            return {"error": "No result data found in SQL Agent response"}
        
        # Extract information from artifacts
        data = {}
        for artifact in task.artifacts:
            for part in artifact.parts:
                if part.type == "text":
                    # Try to parse the text as JSON
                    try:
                        part_data = json.loads(part.text)
                        if isinstance(part_data, dict):
                            # This might be the SQLResultMessage
                            if "sql_query" in part_data and "result" in part_data:
                                data["sql_query"] = part_data["sql_query"]
                                data["result"] = part_data["result"]
                                data["metadata"] = part_data.get("metadata", {})
                    except json.JSONDecodeError:
                        # Store as query if not JSON
                        data["query"] = part.text
                elif part.type == "data":
                    # Direct data part
                    if "sql_query" in part.data and "result" in part.data:
                        data["sql_query"] = part.data["sql_query"]
                        data["result"] = part.data["result"]
                        data["metadata"] = part.data.get("metadata", {})
        
        # If we don't have a query yet, try to get it from the task message
        if "query" not in data and task.status.message:
            for part in task.status.message.parts:
                if part.type == "text":
                    data["query"] = part.text
                    break
        
        return data
    
    async def _send_to_excel_agent(
        self, 
        query: str, 
        sql_query: str, 
        result: List[Dict[str, Any]],
        format_options: Dict[str, Any], 
        session_id: str
    ) -> Dict[str, Any]:
        """Send SQL result to Excel Agent for processing"""
        logger.info(f"Sending SQL result to Excel Agent with {len(result)} records")
        
        # Prepare the request data
        excel_request = {
            "query": query,
            "sql_query": sql_query,
            "result": result,
            "format_options": format_options or {}
        }
        
        task_id = str(uuid.uuid4())
        message = Message(
            role="user",
            parts=[DataPart(data=excel_request)]
        )
        
        task_params = TaskSendParams(
            id=task_id,
            sessionId=session_id,
            message=message,
            acceptedOutputModes=["text", "file"]
        )
        
        try:
            task = await self.excel_client.send_task(task_params)
            logger.info(f"Excel Agent task completed with status: {task.status.state}")
            
            return {
                "status": task.status.state,
                "task": task
            }
        except Exception as e:
            logger.error(f"Error sending task to Excel Agent: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _extract_excel_file_info(self, excel_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Excel file information from Excel Agent response"""
        task = excel_result.get("task")
        if not task or not task.artifacts or not task.artifacts[0].parts:
            return {"error": "No file data found in Excel Agent response"}
        
        file_info = {}
        
        for artifact in task.artifacts:
            for part in artifact.parts:
                if part.type == "file":
                    file_info["name"] = part.file.name
                    file_info["mime_type"] = part.file.mimeType
                    if part.file.bytes:
                        file_info["has_content"] = True
                    if part.file.uri:
                        file_info["uri"] = part.file.uri
                    
                    file_info["metadata"] = part.metadata if hasattr(part, "metadata") else {}
                elif part.type == "text" and "file_info" not in file_info:
                    file_info["description"] = part.text
        
        return file_info

# Command-line interface for testing
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="SQL to Excel Workflow")
    parser.add_argument("--sql-agent", default="http://localhost:10000", help="SQL Agent URL")
    parser.add_argument("--excel-agent", default="http://localhost:10001", help="Excel Agent URL")
    parser.add_argument("--query", required=True, help="Natural language query to process")
    parser.add_argument("--output", default="./outputs", help="Output directory")
    
    args = parser.parse_args()
    
    async def main():
        workflow = SQLExcelWorkflow(
            sql_agent_url=args.sql_agent,
            excel_agent_url=args.excel_agent,
            output_dir=args.output
        )
        
        result = await workflow.process_query(
            query=args.query,
            format_options={"style_template": "professional"}
        )
        
        print(json.dumps(result, indent=2))
    
    asyncio.run(main()) 