from typing import Any, Dict, List, Optional, Literal, AsyncIterable
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage

from core.config import settings
from core.database import db
from core.schema import schema_manager
from core.models import QueryRequest, QueryResponse, SQLResultMessage

memory = MemorySaver()

@tool("list_tables")
def list_tables() -> List[str]:
    """Returns all table names of the database"""
    return schema_manager.get_tables()

@tool("get_table_schema")
def get_table_schema(table_name: str) -> Dict[str, Any]:
    """
    Returns schema information of the specified table.
    """
    full_schema: Dict[str, Dict[str, Any]] = schema_manager.get_schema()
    return {table_name: full_schema.get(table_name, {})}

@tool("get_table_samples")
def get_table_samples(table_name: str) -> Dict[str, Any]:
    """
    Returns up to 5 sample rows for the specified table.
    """
    rows: List[Dict[str, Any]] = schema_manager.get_table_sample_data(table_name, limit=5)
    return {table_name: rows}

@tool("text_to_sql")
def text_to_sql(nl_query: str) -> str:
    """
    Convert natural language query to SQL query.
    Check DB schema internally, request LLM to convert query.
    """
    schema_str = schema_manager.get_schema_as_string()
    prompt = (
        f"You are a SQL expert. Given the database schema:\n"
        f"{schema_str}\n\n"
        f"Convert the following natural language request into a syntactically correct SQL query.\n"
        f"Only output the SQL, without explanations.\n\n"
        f"Request: {nl_query}"
    )
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001")
    sql = llm.predict(prompt)
    return sql.strip()

@tool("execute_sql")
def execute_sql(sql_query: str) -> SQLResultMessage:
    """
    Execute SQL query and return results.
    Returns message in error field when error occurs.
    """
    try:
        rows = db.execute_query(sql_query)
        return SQLResultMessage(
            sql_query=sql_query,
            result=rows,
            error=None,
            metadata={"row_count": len(rows)}
        )
    except Exception as e:
        return SQLResultMessage(
            sql_query=sql_query,
            result=[],
            error=str(e),
            metadata={}
        )
    
class DBAgentResponse(BaseModel):
    status: Literal["input_required", "completed", "error"]
    content: Any

class SQLAgent:
    SYSTEM_INSTRUCTION = (
        "You are a sqecialized assistant for database conversations."
        "Your sole purpose is to use `provided tools` in order to answer questions about database"
        "<provided tools>\n"
        "1) list_tables\n"
        "2) get_table_schema\n"
        "3) (optional) get_table_samples\n"
        "4) text_to_sql\n"
        "5) execute_sql\n"
        "Do not attempt to answer unrelated questions or use tools for other purposes.\n"
        "Set response status to input_required if the user needs to provide more information.\n"
        "Set response status to error if there is an error while processing the request.\n"
        "Set response status to completed if the request is complete.\n"
        "Return only JSON matching the QueryResponse model when completed.\n"
    )
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001")
        self.tools = [list_tables, get_table_schema, get_table_samples, text_to_sql, execute_sql]

        self.graph = create_react_agent(
            self.model, tools=self.tools, checkpointer=memory, prompt = self.SYSTEM_INSTRUCTION, response_format=DBAgentResponse
        )

    def invoke(self, query, sessionId) -> DBAgentResponse:
        config = {"configurable": {"thread_id": sessionId}}
        self.graph.invoke({"messages": [("user", query)]}, config)        
        return self.get_agent_response(config)
    
    async def stream(self, query, sessionId) -> AsyncIterable[Dict[str, Any]]:
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": sessionId}}

        for item in self.graph.stream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Looking up the exchange rates...",
                }
            elif isinstance(message, ToolMessage):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Processing the exchange rates..",
                }            
        
        yield self.get_agent_response(config)


    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)        
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(structured_response, DBAgentResponse): 
            if structured_response.status == "input_required":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.content
                }
            elif structured_response.status == "error":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.content
                }
            elif structured_response.status == "completed":
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": structured_response.content
                }

        return {
            "is_task_complete": False,
            "require_user_input": True,
            "content": "We are unable to process your request at the moment. Please try again.",
        }

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]