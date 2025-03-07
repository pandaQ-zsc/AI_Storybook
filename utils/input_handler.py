# utils/input_handler.py
import re

# def get_user_input():
    # theme = input("请输入绘本主题（例如：太空冒险）: ")
    # style = input("请输入绘画风格（例如：卡通水彩）: ")
    # page_count = int(input("请输入绘本页数（建议4-8页）: "))
    # return {
    #     "theme": theme,
    #     "style": style,
    #     "page_count": page_count
    # }
# utils/input_handler.py
def get_user_input():
    theme = input("请输入绘本主题（如：太空冒险）: ").strip()
    style_options = ["卡通", "水彩", "3D"]
    style = input(f"请选择绘画风格 {style_options}（默认卡通）: ").strip() or "卡通"
    page_count = int(input("请输入页数（4-8页）: ") or 4)
    return {"theme": theme, "style": style, "page_count": page_count}

def split_story(story_text, page_count):
    """将故事文本按段落分割为指定页数"""
    paragraphs = re.split(r'\n\n+', story_text)
    return [para for para in paragraphs if para][:page_count]
