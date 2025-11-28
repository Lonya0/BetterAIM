# Better AIM React 前端版本

Better AIM的React前端实现，替代原有的Gradio界面，提供更好的用户体验和扩展性。

## 🚀 快速开始

### 环境要求

- Python 3.8+ (推荐版本3.10)
- Node.js 16+ (用于前端开发，建议版本22+)
- npm 或 yarn

### 安装步骤

1. **安装Python依赖**
```bash
pip install .
pip install -r react_requirements.txt
```

2. **安装前端依赖**
```bash
cd frontend
npm install
```

### 启动方式

#### 启动前需要配置环境变量！
```bash
export API_KEY=your-api-key
```

#### 方式一：使用示例配置启动（推荐）
```bash
cd example/DeePTB-agent
python react_api.py
```

#### 方式二：使用默认配置启动
```bash
python -m better_aim.react_main
```

#### 方式三：使用命令行参数
```bash
python -m better_aim.react_main \
    --port 8000 \
    --host 0.0.0.0 \
    --frontend-port 50001 \
    --frontend-host 0.0.0.0 \
    --mcp_tools http://0.0.0.0:50001/sse \
    --api-key your_api_key
```

### 命令行参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--port`, `-p` | 8000 | 后端API服务器端口号 |
| `--host`, `-l` | 0.0.0.0 | 后端API服务器主机地址 |
| `--frontend-port`, `-fp` | 3000 | 前端开发服务器端口号 |
| `--mcp_tools` | http://0.0.0.0:50001/sse | MCP工具服务器链接 |
| `--api-key` | - | API密钥 |
| `--no-dev` | False | 不启动前端开发服务器，使用生产模式 |
| `--debug` | False | 开启调试模式 |

## 📁 项目结构

```
better_aim/
├── react_host.py           # FastAPI后端服务器
├── react_main.py          # React版本启动入口
└── ...                   # 其他现有文件

frontend/
├── src/
│   ├── components/        # React组件
│   │   ├── Login/        # 登录界面
│   │   ├── Chat/         # 聊天界面
│   │   ├── FilePanel/    # 文件管理面板
│   │   ├── ParamPanel/   # 参数修改面板
│   │   └── SessionPanel/ # 会话管理面板
│   ├── contexts/         # React Context状态管理
│   ├── services/         # API服务层
│   ├── types/           # TypeScript类型定义
│   └── utils/           # 工具函数
├── package.json          # 前端依赖配置
└── vite.config.ts        # Vite构建配置
```

## 🎯 功能特性

### ✅ 已实现功能

1. **登录界面**
   - 32位会话ID输入和随机生成
   - 响应式设计，适配移动端
   - 服务状态显示

2. **主聊天界面**
   - 左右分栏消息展示（用户/助手）
   - 实时流式响应
   - Markdown渲染和代码高亮
   - 示例对话选择（选择后填充，不直接发送）
   - 回车发送消息

3. **文件管理面板**
   - 显示`/tmp/[session_id]`目录文件
   - 拖拽上传和点击上传
   - 文件下载功能
   - 文件大小显示和格式化

4. **参数修改面板**
   - 在线/玻尔模式切换
   - 逐个修改/JSON编辑双模式
   - 动态表单生成
   - 实时参数拦截和修改

5. **会话管理面板**
   - 会话历史列表
   - 会话标题编辑
   - 会话切换功能
   - 消息统计和最后活跃时间

### 🔄 MCP工具拦截机制

完整复现了原有Gradio版本的MCP工具拦截流程：

1. Agent调用工具时触发`tool_modify_guardrail`
2. 后端通过WebSocket向前端推送参数修改请求
3. 前端显示参数修改界面，暂停agent执行
4. 用户修改参数后提交，恢复agent执行
5. 使用修改后的参数继续工具调用

## 🛠️ 开发模式

### 前端开发
```bash
cd frontend
npm run dev
```

### 后端开发
```bash
python -m better_aim.react_main --no-dev
```

### 生产构建
```bash
cd frontend
npm run build
```

## 🔧 配置说明

### 环境变量
修改 `.env` 文件来配置服务器：

```bash
# API密钥配置 - 请替换为您的实际API密钥
API_KEY=your_api_key_here

# 服务器配置
HOST=0.0.0.0                    # 后端监听地址
PORT=8000                         # 后端端口
FRONTEND_HOST=0.0.0.0            # 前端监听地址
FRONTEND_PORT=50001                 # 前端端口
BACKEND_HOST=0.0.0.0              # 前端代理的后端地址
BACKEND_PORT=8000                   # 前端代理的后端端口
```

- `API_KEY`: LLM API密钥
- `HOST`: 后端服务器监听地址
- `PORT`: 后端服务器端口
- `FRONTEND_HOST`: 前端服务器监听地址
- `FRONTEND_PORT`: 前端服务器端口
- `BACKEND_HOST`: 前端代理到的后端地址
- `BACKEND_PORT`: 前端代理到的后端端口

### agent_info配置
```python
agent_info = {
    "name": "Your-Agent-Name",
    "description": "Agent描述",
    "instruction": "Agent指令"
}
```

### model_config配置
```python
model_config = {
    'model': "openai/qwen3-max",
    'api_base': "https://llm.dp.tech",
    'api_key': "your_api_key"
}
```

### tools_need_modify配置
```python
tools_need_modify = ["tool_name_1", "tool_name_2"]
```

## 🚨 注意事项

1. **版本兼容性**: 确保所有依赖包版本兼容，建议使用较新版本
2. **文件权限**: 确保`/tmp`目录有读写权限
3. **网络配置**: 检查MCP服务器连接和防火墙设置
4. **API密钥**: 确保API密钥有效且有足够权限

## 🐛 故障排除

### 常见问题

1. **WebSocket连接失败**
   - 检查端口是否被占用
   - 确认防火墙设置
   - 查看浏览器控制台错误信息

2. **文件上传失败**
   - 检查文件大小限制（10MB）
   - 确认目录权限
   - 查看后端日志

3. **MCP工具拦截不工作**
   - 确认工具名称在`tools_need_modify`列表中
   - 检查`tool_modify_guardrail.py`配置
   - 查看WebSocket消息流

4. **前端构建失败**
   - 清除node_modules重新安装
   - 检查Node.js版本
   - 查看构建错误日志

### 调试模式
```bash
python -m better_aim.react_main --debug
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目遵循原有项目的许可证。