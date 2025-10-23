from better_aim import launch
import os

agent_info = {
    "name": "Abacus-agent",
    "description": "a",
    "instruction": """You are an expert in AI and computational materials science. 
Help users perform DeePTB tasks including training config file generation, submitting training missions, generating baseline models, and testing."""
}

mcp_server_url = "http://0.0.0.0:50001/sse"

model_config = {
    'model': "deepseek/deepseek-chat",
    'api_base': "https://api.deepseek.com",
    'api_key': os.getenv("API_KEY")
}

launch(agent_info=agent_info,
       debug_mode=True,
       mcp_server_url=mcp_server_url,
       model_config=model_config)
