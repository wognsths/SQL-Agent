import pathlib, json
from fastapi import FastAPI
from common.server.server import A2AServer
from common.types import AgentCard           # ◀ AgentCard 모델
from .task_manager import RouteTaskManager

# 1) JSON 파일 → 객체
card_path = pathlib.Path(__file__).parent / "agent_card.json"
agent_card = AgentCard.model_validate_json(card_path.read_text())

# 2) 객체 전달
server = A2AServer(
    agent_card=agent_card,                   # ✅ Pydantic 객체
    task_manager=RouteTaskManager(),
)

app = FastAPI(title="Route Agent (A2A)")
app.mount("/", server.app)                   # Starlette 앱 마운트