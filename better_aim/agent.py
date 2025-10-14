from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
import os
#from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

def mcp_tools(mcp_tools_url):
    return MCPToolset(
        connection_params=SseServerParams(url=mcp_tools_url)
    )

model_config = {
    'model': os.getenv("DEEPSEEK_MODEL_NAME"),
    'api_base': os.getenv("DEEPSEEK_API_BASE"),
    'api_key': os.getenv("DEEPSEEK_API_KEY")
}

def create_llm_agent(session_id: str, mcp_tools_url: str, agent_info: dict) -> LlmAgent:
    """根据用户信息创建LlmAgent"""

    agent = LlmAgent(
        model=LiteLlm(**model_config),
        name=f"{agent_info['name'].replace('-','_')}_{session_id}",
        description=agent_info['description'],
        instruction=agent_info['instruction'],
        tools=[mcp_tools(mcp_tools_url=mcp_tools_url)]
    )

    return agent


