import json
import logging
from langchain_openai import ChatOpenAI

from .prompts import ROUTE_AGENT_PROMPT
from .utils import parse_route_agent_response
from core.config import settings

logger = logging.getLogger(__name__)

class RouteAgent:
    """Stateless Routing Agent – query in → decision out"""

    def __init__(self, model: str | None = None, temperature: float = 0.1):
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=model or settings.OPENAI_MODEL,
            temperature=temperature,
        )
        # LangChain Runnable (prompt → llm → str)
        self.chain = ROUTE_AGENT_PROMPT | self.llm

    async def aroute(self, *, user_query: str, state: dict | None = None) -> dict:
        """Async interface (Used in A2A TaskManager)"""
        payload = {
            "query": user_query,
            "state_json": json.dumps(state or {}),
        }
        logger.info("Routing query: %s", user_query)
        resp = await self.chain.apredict(payload)
        decision = parse_route_agent_response(resp)
        logger.info("Decision: %s", decision)
        return decision