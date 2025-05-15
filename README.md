@Author: BNBU_XQ

# AI故事绘本生成器

一款智能绘本创作平台，基于人工智能技术，根据用户输入的主题自动生成精美插图和故事内容的儿童绘本生成系统。

![image-20250327111712370](./README.assets/image-20250327111712370.png)

## 📋 功能特点

- 🤖 智能故事生成：根据主题自动创作故事情节与内容
- 🎨 AI绘图服务：为每一页自动生成精美插图
- 📄 PDF导出功能：生成带文字和图片的完整PDF绘本
- 🌐 在线阅读体验：支持网页直接浏览绘本内容
- 🖼️ 多种风格选择：提供多种绘图风格满足不同需求
- 👤 用户账户系统：支持用户注册、登录和个人绘本管理

## 💻 技术栈

### 后端
- Python + Flask：轻量级Web框架
- OpenAI API：智能文本生成服务
- 火山引擎AI服务：高质量图像生成
- FPDF2：PDF文件生成与处理

### 前端
- Vue 3 + Vite：现代化前端开发框架
- Element Plus：美观的UI组件库
- Vue Router：前端路由管理
- Axios：HTTP请求处理
- LocalStorage：用户数据本地存储

## 🚀 安装与运行

### 后端设置

1. 创建并激活虚拟环境（可选）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. 安装依赖项
```bash
pip install -r requirements.txt
```

3. 配置环境变量
创建`.env`文件并设置API密钥：
```
VOLC_AK=你的火山引擎AK
VOLC_SK=你的火山引擎SK
ARK_API_KEY=你的火山方舟API密钥
```

4. 启动后端服务
```bash
python app.py
```

### 前端设置

1. 安装依赖项
```bash
cd frontend
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

3. 构建生产版本
```bash
npm run build
```

## 🎮 使用指南

### 账户操作
1. 访问系统首页（默认为 http://localhost:5173）
2. 新用户可点击"立即注册"创建账户
3. 已有账户直接登录系统

### 创建绘本
1. 登录后输入创作主题（例如："宇宙冒险"）
2. 选择绘本风格和页数
3. 点击"生成绘本"按钮
4. 等待系统处理并生成内容
5. 在线浏览或下载PDF版本

## 👥 用户系统

系统支持以下用户操作：
- 账户注册：创建个人用户账号
- 用户登录：使用已注册账户访问系统
- 管理员账户：预设管理员可直接登录系统

用户数据使用浏览器localStorage存储，确保用户信息安全性。

## 🔗 相关链接

- [北师港浸大官网](https://www.uic.edu.cn)
- [项目演示视频](../AIGC绘本生成器.mov)

## 📝 开发者信息

- 开发者：BNBU_XQ
- 版本：1.0.0
- 最后更新：2025-05-15
