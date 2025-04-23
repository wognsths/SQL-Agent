from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities, AgentSkill, MissingAPIKeyError
from common.utils.push_notification_auth import PushNotificationSenderAuth
from agents.sql_agent.task_manager import AgentTaskManager
from agents.sql_agent.agent import SQLAgent
import click
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getlogger(__name__)

@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10000)
def main(host, port):
    """Starts the SQL agent server."""
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")
        
        capabilities = AgentCapabilities(streaming=True, pushNotifications=True)
        skill = AgentSkill(
            id="text_to_sql",
            description="Helps with convert natural language query to SQL query, and approach to database",
            tags=["text-to-sql", "database manage"],
            examples=["I want to get data related to eletric machine from the database"]
        )
        agent_card = AgentCard(
            name="Database Agent",
            description="Helps with convert natural language query to SQL query, and approach to database",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=SQLAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=SQLAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        notification_sender_auth = PushNotificationSenderAuth()
        notification_sender_auth.generate_jwk()
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(
                agent=SQLAgent(),
                notification_sender_auth=notification_sender_auth
                ),
            host=host,
            port=port,
        )

        server.app.route(
            "/.well-known/jwks.json", notification_sender_auth.handle_jwks_endpoint, methods=["GET"]
        )

        logger.info(f"Starting server on {host}:{port}")
        server.start()
    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()