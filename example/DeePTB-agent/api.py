from better_aim import launch

agent_info = {
    "name": "DeePTB-agent",
    "description": "a",
    "instruction": "b"
}

mcp_tools_url = "http://0.0.0.0:50001/sse"

launch(agent_info=agent_info,
       debug_mode=True,
       mcp_tools_url=mcp_tools_url)
