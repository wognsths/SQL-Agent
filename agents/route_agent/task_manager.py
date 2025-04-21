from common.server.task_manager import InMemoryTaskManager
from common.types import TextPart
import json

from .agent import RouteAgent


class RouteTaskManager(InMemoryTaskManager):
    def __init__(self):
        super().__init__()
        self.router = RouteAgent()

    async def on_send_task(self, req):
        """Handle /tasks/send"""
        user_txt = req.message.parts[0].text
        # PENDING → WORKING
        self.update_status(req.id, state="working", message="routing")

        decision = await self.router.aroute(user_query=user_txt)
        next_agent = decision.get("next_agent", "unknown")

        txt = (
            f"route_decision: {next_agent}\n"
            f"metadata: {json.dumps(decision, ensure_ascii=False)}"
        )
        part = TextPart(text=txt)
        # WORKING → COMPLETED
        self.complete(req.id, parts=[part])
    
    async def on_send_task_subscribe(self, req):
        """Return an async iterator that streams status updates.."""
        return self.subscribe(req.task_id)