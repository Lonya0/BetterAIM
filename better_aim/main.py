from google.adk.agents import LlmAgent
from better_aim.host import create_interface
import os
import argparse
import sys
from typing import Dict
from dotenv import load_dotenv


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="DPTB Agent 启动程序")

    parser.add_argument(
        "--port", "-p",
        type=int,
        default=50005,
        help="服务器端口号 (默认: 50005)"
    )

    parser.add_argument(
        "--host", "-l",
        type=str,
        default="0.0.0.0",
        help="服务器主机地址 (默认: 0.0.0.0)"
    )

    parser.add_argument(
        "--mcp_tools",
        type=str,
        default="http://0.0.0.0:50001/sse",
        help="DeePTB agent tools 的 mcp tools链接 (默认: http://0.0.0.0:50001/sse)"
    )

    parser.add_argument(
        "--share", "-s",
        action="store_true",
        help="是否生成公共分享链接 (默认: False)"
    )

    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Gradio开启debug模式 (默认: False)"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="Google API密钥 (优先级高于环境变量)"
    )

    return parser.parse_args()

def launch(agent_info: dict,
           host: str="0.0.0.0",
           port: int=50005,
           share_mode: bool=False,
           debug_mode: bool=False,
           mcp_tools_url: str="http://0.0.0.0:50001/sse",
           api_key: str=None,
           work_path: str='/tmp'):
    # 设置API密钥（命令行参数优先）
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    elif not os.getenv("GOOGLE_API_KEY"):
        print("警告: GOOGLE_API_KEY环境变量未设置，请通过--api-key参数设置或设置环境变量")

    # 创建并启动界面
    demo = create_interface(mcp_tools_url=mcp_tools_url, agent_info=agent_info, work_path=work_path)
    os.chdir(work_path)

    print(f"启动参数: 主机={host}, 端口={port}, 分享={share_mode}, 调试={debug_mode}, 工作路径={work_path}")

    try:
        demo.launch(
            server_name=host,
            server_port=port,
            share=share_mode,
            debug=debug_mode
        )
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    if load_dotenv():
        print("环境变量已根据`.env`文件读入")
    else:
        print("未找到`.env`文件或无任何变量被读入")

    args = parse_arguments()

    launch()




if __name__ == "__main__":
    main()