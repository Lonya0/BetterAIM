import gradio as gr
import json
import os
from typing import Dict, List, Tuple
from better_aim.agent import create_llm_agent
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio

from better_aim.utils import generate_random_string

session_service = InMemorySessionService()

# 全局变量存储活跃的agents
active_agents: Dict[str, LlmAgent] = {}


history_file_path = './chat_history'


def get_chat_history_file_path(sha_id: str) -> str:
    """获取聊天历史文件路径"""
    # 确保文件路径存在
    os.makedirs(history_file_path, exist_ok=True)
    return os.path.join(history_file_path, f"{sha_id[:16]}.json")


def load_chat_history(sha_id: str) -> List[List[str]]:
    """加载聊天历史记录"""
    history_file = get_chat_history_file_path(sha_id)

    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_chat_history(sha_id: str, history: List[List[str]]):
    """保存聊天历史记录"""
    history_file = get_chat_history_file_path(sha_id)

    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存聊天历史失败: {e}")


def login(session_id: str, mcp_tools_url: str, agent_info: dict) -> Tuple[
    gr.update, gr.update, str, List[List[str]]]:
    """处理登录逻辑"""

    if not session_id:
        return gr.update(visible=True), gr.update(visible=False), "请填写或自动生成会话ID", []
    elif len(session_id) != 20:
        return gr.update(visible=True), gr.update(visible=False), f"会话ID需要为长度为20的任意字符，目前长度：{len(session_id)}", []

    # 生成SHA ID
    sha_id = session_id

    # 创建或获取agent
    if sha_id not in active_agents:
        try:
            agent = create_llm_agent(session_id, mcp_tools_url, agent_info=agent_info)
            active_agents[sha_id] = agent
        except Exception as e:
            return gr.update(visible=True), gr.update(visible=False), f"创建Agent失败: {str(e)}", []
    else:
        agent = active_agents[sha_id]

    # 加载聊天历史
    chat_history = load_chat_history(sha_id)

    # 返回更新后的界面和状态
    return (
        gr.update(visible=False),  # 隐藏登录界面
        gr.update(visible=True),  # 显示聊天界面
        f"登录成功! 会话 ID: {'*' * 16 + sha_id[:4]}",  # 状态消息
        chat_history  # 聊天历史
    )

# from https://google.github.io/adk-docs/tutorials/agent-team/#step-1-your-first-agent-basic-weather-lookup
async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    #print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response." # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # You can uncomment the line below to see *all* events during execution
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            # Add more checks here if needed (e.g., specific error codes)
            break # Stop processing events once the final response is found

    #print(f"<<< Agent Response: {final_response_text}")
    return final_response_text

async def chat_with_agent(message: str, history: List[List[str]], session_id: str, agent_info: dict) -> Tuple[
    List[List[str]], str]:
    """处理与agent的聊天"""
    if session_id not in active_agents:
        return history, "Agent未找到，请重新登录"

    agent = active_agents[session_id]
    session = await session_service.create_session(app_name=agent_info["name"],
                                   user_id=session_id[:4],
                                   session_id=session_id)

    runner = Runner(agent=agent,
                    app_name=agent_info["name"],
                    session_service=session_service)

    final_response_text = await call_agent_async(query=message, runner=runner, user_id=session_id[:4], session_id=session_id)

    # 更新聊天历史
    new_history = history + [[message, final_response_text]]

    # 保存聊天历史
    save_chat_history(session_id, new_history)

    return new_history, ""



def logout() -> Tuple[gr.update, gr.update, str, List[List[str]], str]:
    """处理登出逻辑"""
    return (
        gr.update(visible=True),  # 显示登录界面
        gr.update(visible=False),  # 隐藏聊天界面
        "已登出",  # 状态消息
        [],  # 清空聊天历史
        ""# 清空登录表单
    )

def create_interface(mcp_tools_url: str, agent_info: dict):
    """创建Gradio界面"""
    with gr.Blocks(title=agent_info["name"], theme=gr.themes.Soft()) as demo:
        # 状态变量
        session_id_state = gr.State("")
        mcp_tools_url_state = gr.State(mcp_tools_url)
        agent_info_state = gr.State(agent_info)

        gr.Markdown(f"# {agent_info['name']}")

        with gr.Column(visible=True) as login_section:
            gr.Markdown("## 创建会话")

            with gr.Row(equal_height=True):
                session_id = gr.Textbox(label="会话ID", placeholder="请输入20位任意字符串", scale=4)
                generate_btn = gr.Button("随机生成", scale=1, min_width=100, variant="primary")

            gr.Markdown("输入或自动生成20位任意字符串作为您的专属会话ID，使用相同ID可以访问此前的历史记录，历史记录在一小时后会被自动清除，请不要传播您专属的ID！")

            login_btn = gr.Button("进入会话", variant="primary")

            status_msg = gr.Textbox(label="状态", interactive=False)

        with gr.Column(visible=False) as chat_section:
            with gr.Row():
                with gr.Column(scale=2) as main_column:
                    gr.Markdown(f"## 与{agent_info['name']}协作")

                    # 显示当前用户和项目信息
                    current_info = gr.Textbox(
                        label="当前会话信息",
                        interactive=False,
                        value=""
                    )

                    chatbot = gr.Chatbot(
                        label="聊天记录",
                        height=900,
                        show_copy_button=True
                    )

                    with gr.Row(equal_height=True):
                        msg = gr.Textbox(
                            label="输入消息",
                            placeholder=f"输入你想对{agent_info['name']}说的话...",
                            scale=4
                        )
                        send_btn = gr.Button("发送", variant="primary", scale=1)

                    with gr.Row():
                        clear_btn = gr.Button("清空对话")
                        logout_btn = gr.Button("离开会话", variant="secondary")

                    chat_status = gr.Textbox(label="聊天状态", interactive=False)

                with gr.Column(scale=1) as values_column:
                    gr.Markdown("## 修改运行参数")
                    gr.Text(value="当调用mcp工具时，将会弹出参数的确认或手动修改")

        def on_generate_click():
            """当生成按钮被点击时的回调函数"""
            return generate_random_string()

        generate_btn.click(
            fn=on_generate_click,
            outputs=session_id
        )
        # 更新会话信息显示
        def update_session_info(sha, username, project_id, file_path):
            if sha:
                return f"用户: {username} | 项目ID: {project_id} | 文件路径: {file_path}"
            return "未登录"

        # 登录按钮事件
        login_btn.click(
            fn=login,
            inputs=[session_id, mcp_tools_url_state, agent_info_state],
            outputs=[login_section, chat_section, status_msg, chatbot]
        ).then(
            lambda _session_id:
            ({"session_id": _session_id},
             f"会话ID: {_session_id}"),
            inputs=[session_id],
            outputs=[session_id_state, current_info]
        )

        # 发送消息事件
        async def handle_send_message(message, history, _session_id):
            if not message.strip():
                return history, "消息不能为空"
            new_history, status = await chat_with_agent(message, history, session_id=_session_id, agent_info=agent_info)
            return new_history, status

        send_btn.click(
            fn=handle_send_message,
            inputs=[msg, chatbot, session_id_state],
            outputs=[chatbot, chat_status]
        ).then(
            lambda: "",  # 清空输入框
            outputs=msg
        )

        # 回车发送消息
        msg.submit(
            fn=handle_send_message,
            inputs=[msg, chatbot, session_id_state],
            outputs=[chatbot, chat_status]
        ).then(
            lambda: "",  # 清空输入框
            outputs=msg
        )

        # 清空对话
        clear_btn.click(
            fn=lambda sha: ([], "对话已清空"),
            inputs=[session_id_state],
            outputs=[chatbot, chat_status]
        )

        # 登出按钮事件
        logout_btn.click(
            fn=logout,
            outputs=[
                login_section,
                chat_section,
                status_msg,
                chatbot
            ]
        ).then(
            lambda: ("", "", "", "", "未登录"),  # 清空状态
            outputs=[session_id_state, current_info]
        )

    return demo
