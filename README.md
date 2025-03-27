@Author: 熊强

# AI故事绘本生成器

这是一个基于AI的儿童绘本生成系统，可以根据输入的主题自动生成配有精美插图的绘本。

## 功能特点

- 根据主题自动生成故事内容
- AI绘图生成每页插图
- 生成带文字的PDF文件
- 在线浏览生成的绘本
- 支持多种绘图风格

## 技术栈

### 后端
- Python + Flask
- OpenAI API（文本生成）
- 火山引擎AI服务（图像生成）
- FPDF2（PDF生成）

### 前端
- Vue 3 + Vite
- Element Plus UI组件库
- Vue Router
- Axios

## 安装与运行

### 后端

1. 创建并激活虚拟环境（可选）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. 安装依赖
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

### 前端

1. 安装依赖
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

## 使用方法

1. 访问前端页面（默认为 http://localhost:5173）
2. 输入创作主题（例如："宇宙冒险"）
3. 选择绘本风格和页数
4. 点击"生成绘本"按钮
5. 等待生成完成后查看绘本内容
6. 可以下载PDF版本或在线浏览