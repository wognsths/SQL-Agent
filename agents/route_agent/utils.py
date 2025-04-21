import json
import re
from typing import Dict, Any

def parse_route_agent_response(response: str) -> Dict[str, Any]:
    """Parse response of route agent"""
    json_match = re.search(f'```json\s*(.*?)\s*```', response, re.DOTALL)

    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    parsed_data = {}

    next_agent_match = re.search(r'"?next_agent"?:\s*"(.*?)"', response, re.DOTALL)
    if next_agent_match:
        parsed_data["next_agent"] = next_agent_match.group(1).strip()

    query_analysis_match = re.search(r'"?query_analysis"?:\s*"(.*?)"', response, re.DOTALL)
    if query_analysis_match:
        parsed_data["query_analysis"] = query_analysis_match.group(1).strip()

    execution_plan_match = re.search(r'"?execution_plan"?:\s*"(.*?)"', response, re.DOTALL)
    if execution_plan_match:
        parsed_data["execution_plan"] = execution_plan_match.group(1).strip()

    metadata_match = re.search(r'"?metadata"?:\s*"(.*?)"', response, re.DOTALL)
    if metadata_match:
        parsed_data["metadata"] = metadata_match.group(1).strip()
    
    return parsed_data
