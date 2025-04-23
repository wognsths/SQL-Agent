from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities, AgentSkill, MissingAPIKeyError
from common.utils.push_notification_auth import PushNotificationSenderAuth
from excel_agent.task_manager import ExcelAgentTaskManager
from excel_agent.agent import ExcelAgent
import click
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10001)
def main(host, port):
    """Starts the Excel agent server."""
    try:
        capabilities = AgentCapabilities(streaming=False, pushNotifications=True)
        
        skill = AgentSkill(
            id="sql_to_excel",
            name="SQL to Excel Conversion",
            description="Converts SQL query results to formatted Excel files",
            tags=["excel", "sql", "data-export", "spreadsheet"],
            examples=[
                "Export these SQL results to Excel",
                "Create a spreadsheet with this data",
                "Format this query result as an Excel file"
            ]
        )
        
        agent_card = AgentCard(
            name="Excel Export Agent",
            description="Converts SQL query results to formatted Excel files with various styling options",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=["text", "data"],
            defaultOutputModes=ExcelAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        notification_sender_auth = PushNotificationSenderAuth()
        notification_sender_auth.generate_jwk()
        
        # Create outputs directory if it doesn't exist
        os.makedirs(os.path.join(os.getcwd(), "outputs", "excel"), exist_ok=True)
        
        server = A2AServer(
            agent_card=agent_card,
            task_manager=ExcelAgentTaskManager(
                agent=ExcelAgent(),
                notification_sender_auth=notification_sender_auth
            ),
            host=host,
            port=port,
        )

        server.app.route(
            "/.well-known/jwks.json", notification_sender_auth.handle_jwks_endpoint, methods=["GET"]
        )

        logger.info(f"Starting Excel Agent server on {host}:{port}")
        server.start()
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()
