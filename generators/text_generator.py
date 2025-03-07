# generators/text_generator.py
import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

# 初始化火山引擎客户端
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_story(params):
    """
    通过火山引擎方舟平台生成儿童故事
    参数格式：
    {
        "theme": "太空冒险",
        "style": "卡通",
        "page_count": 4
    }
    """
    try:
        # 构建系统提示词
        system_prompt = """你是一位专业的儿童文学作家，擅长创作适合绘本的短篇故事。请严格按照以下要求创作："""

        # 构建用户提示词
        user_prompt = f"""
        创作主题：{params['theme']}
        风格要求：{params['style']}风格
        字数限制：{params['page_count']*80}-{params['page_count']*120}字
        格式要求：
        1. 明确分为{params['page_count']}个段落，每段以【PAGE】标记开头
        2. 每段包含3-5个可视化元素（用[]标记，如[彩虹滑梯]）
        3. 包含简单对话（用「」标记）
        4. 最后追加JSON格式的可视化标签：
        {{"colors": ["主色1", "主色2"], "objects": ["关键物体1", "关键物体2"]}}
        """

        # 调用方舟平台API
        completion = client.chat.completions.create(
            model="ep-20250306152138-g824j",  # 替换为实际接入点ID
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=1200
        )

        # 解析响应内容
        raw_text = completion.choices[0].message.content

        # 提取可视化标签
        if "{" in raw_text and "}" in raw_text:
            try:
                json_start = raw_text.rfind("{")
                json_end = raw_text.rfind("}") + 1
                visual_tags = json.loads(raw_text[json_start:json_end])
                story_content = raw_text[:json_start].strip()
            except json.JSONDecodeError:
                visual_tags = None
                story_content = raw_text
        else:
            visual_tags = None
            story_content = raw_text

        # 分页处理
        pages = []
        current_page = []
        for line in story_content.split("\n"):
            if line.startswith("【PAGE】"):
                if current_page:
                    pages.append(" ".join(current_page))
                    current_page = []
                current_page.append(line.replace("【PAGE】", "").strip())
            else:
                current_page.append(line.strip())
        if current_page:
            pages.append(" ".join(current_page))

        # 确保页数匹配
        pages = pages[:params["page_count"]]
        while len(pages) < params["page_count"]:
            pages.append("（本页内容待补充）")

        return {
            "pages": pages,
            "visual_tags": visual_tags or {"colors": [], "objects": []},
            "raw_data": completion.model_dump()  # 保留原始响应数据
        }

    except Exception as e:
        logger.error(f"故事生成失败: {str(e)}")
        return None

# 单元测试
if __name__ == "__main__":
    # 测试配置
    test_params = {
        # "theme": "海底探险",
        # "style": "奇幻水彩",
        # "page_count": 3
        "theme": "星球冒险",
        "style": "海洋",
        "page_count": 3
    }

    result = generate_story(test_params)
    if result:
        print("生成成功！")
        for i, page in enumerate(result["pages"]):
            print(f"\n=== 第{i+1}页 ===")
            print(page)
        print("\n可视化标签:", json.dumps(result["visual_tags"], indent=2,ensure_ascii=False))
    else:
        print("生成失败")
