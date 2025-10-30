import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

def mcp_tools_server(mcp_tools_url):
    return MCPServerSSE(mcp_tools_url)

def openai_model(model_name:str,
                 api_key:str = None,
                 base_url:str = None):
    return OpenAIChatModel(model_name, provider=OpenAIProvider(base_url=base_url, api_key=api_key if api_key else os.getenv("API_KEY")))


def create_llm_agent(mcp_tools_url: str, agent_info: dict, model_config: dict) -> Agent:
    """根据用户信息创建LlmAgent"""

    agent = Agent(
        model=openai_model(**model_config),
        system_prompt=agent_info['instruction'] + "when calling mcp tools, do not use named submit_*** tools.",
        toolsets=[mcp_tools_server(mcp_tools_url=mcp_tools_url)]
    )

    return agent


