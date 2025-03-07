# main.py
import json
import logging
from pathlib import Path
from generators.text_generator import generate_story
from generators.image_generator import VolcBookGenerator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_image_prompt(page_text, visual_tags):
    """根据文本内容和可视化标签构建图片生成提示词"""
    # 提取可视化元素
    elements = [item.strip("[]") for item in page_text.split() if item.startswith("[")]

    # 构建提示词
    prompt = f"{visual_tags.get('style', '卡通')}风格，"
    prompt += "，".join(elements)
    prompt += f"，主色调：{','.join(visual_tags.get('colors', []))}"

    # 添加文字标注（如果需要）
    # prompt += "，文字：\"示例文字\" 位置：顶部中央，大小：72px，颜色：#8B4513"

    return prompt

def generate_book(params):
    """生成完整绘本"""
    # 生成故事文本
    story = generate_story(params)
    if not story:
        logger.error("故事生成失败，终止绘本生成")
        return

    # 初始化图片生成器
    image_gen = VolcBookGenerator(output_dir=f"books/{params['theme']}")

    # 创建目录结构
    book_dir = Path(f"books/{params['theme']}")
    book_dir.mkdir(parents=True, exist_ok=True)

    # 保存元数据
    with open(book_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "params": params,
            "visual_tags": story["visual_tags"],
            "raw_data": story["raw_data"]
        }, f, ensure_ascii=False, indent=2)

    # 生成每页内容
    for page_num, page_text in enumerate(story["pages"], 1):
        logger.info(f"正在生成第{page_num}页...")

        # 构建图片生成提示词
        prompt = build_image_prompt(page_text, story["visual_tags"])

        # 生成图片
        result = image_gen.generate_page(
            prompt=prompt,
            page_num=page_num,
            style=story["visual_tags"].get("style", "卡通")
        )

        if not result:
            logger.warning(f"第{page_num}页图片生成失败，跳过...")
            continue

if __name__ == "__main__":
    # 生成参数配置
    book_params = {
        "theme": "海洋星球大冒险",
        "style": "水彩",
        "page_count": 3
    }

    # 执行生成
    generate_book(book_params)