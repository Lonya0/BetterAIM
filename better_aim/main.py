from better_aim.host import create_interface
import os
import argparse
import sys
import asyncio

from better_aim.load_mcp_tools import get_mcp_server_tools


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
           model_config: dict,
           host: str="0.0.0.0",
           port: int=50005,
           share_mode: bool=False,
           debug_mode: bool=False,
           mcp_server_url: str="http://0.0.0.0:50001/sse",
           mcp_server_mode: str="bohr-agent-sdk",
           api_key: str=None,
           work_path: str='/tmp'):
    # 设置API密钥（命令行参数优先）
    if api_key:
        os.environ["API_KEY"] = api_key
        model_config["api_key"] = api_key
    else:
        if os.getenv("API_KEY"):
            model_config["api_key"] = os.getenv("API_KEY")
        else:
            print("警告: API_KEY环境变量未设置，请通过--api-key参数设置或设置环境变量")

    # 加载 mcp server 工具信息
    tools_info = asyncio.run(get_mcp_server_tools(mcp_server_url))
    #print(tools_info)

    # 创建并启动界面
    demo = create_interface(mcp_server_url=mcp_server_url,
                            agent_info=agent_info,
                            work_path=work_path,
                            tools_info=tools_info,
                            model_config=model_config,
                            mcp_server_mode=mcp_server_mode)
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
    args = parse_arguments()

    launch()

if __name__ == "__main__":
    main()