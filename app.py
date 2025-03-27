# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
import json
import logging
from main import generate_book
import shutil

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置静态文件目录
BOOKS_DIR = Path("books")
BOOKS_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/api/generate', methods=['POST'])
def api_generate_book():
    """处理绘本生成请求"""
    try:
        # 获取请求参数
        data = request.json
        theme = data.get('theme', '')
        style = data.get('style', '')
        page_count = int(data.get('page_count', 3))

        if not theme or page_count <= 0:
            return jsonify({"success": False, "message": "参数无效"}), 400

        # 生成绘本
        book_params = {
            "theme": theme,
            "style": style,
            "page_count": page_count
        }

        # 调用主程序生成绘本
        generate_book(book_params)

        # 读取元数据
        book_dir = BOOKS_DIR / theme
        metadata_path = book_dir / "metadata.json"

        if not metadata_path.exists():
            return jsonify({"success": False, "message": "生成失败，请重试"}), 500

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # 获取生成的图片列表
        image_files = [f.name for f in book_dir.glob("page_*.png")]
        image_files.sort()

        # 检查PDF文件是否存在
        pdf_path = book_dir / "book.pdf"
        has_pdf = pdf_path.exists()

        return jsonify({
            "success": True,
            "book_dir": theme,
            "images": image_files,
            "metadata": metadata,
            "has_pdf": has_pdf
        })

    except Exception as e:
        logger.error(f"生成失败: {str(e)}")
        return jsonify({"success": False, "message": f"生成失败: {str(e)}"}), 500

@app.route('/api/books', methods=['GET'])
def list_books():
    """列出所有已生成的绘本"""
    try:
        books = []
        for book_dir in BOOKS_DIR.iterdir():
            if book_dir.is_dir():
                metadata_path = book_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)

                    image_files = [f.name for f in book_dir.glob("page_*.png")]
                    image_files.sort()

                    pdf_path = book_dir / "book.pdf"
                    has_pdf = pdf_path.exists()

                    books.append({
                        "theme": book_dir.name,
                        "images": image_files,
                        "metadata": metadata,
                        "has_pdf": has_pdf
                    })

        return jsonify({"success": True, "books": books})

    except Exception as e:
        logger.error(f"获取绘本列表失败: {str(e)}")
        return jsonify({"success": False, "message": f"获取绘本列表失败: {str(e)}"}), 500

@app.route('/api/books/<theme>/images/<filename>', methods=['GET'])
def get_book_image(theme, filename):
    """获取绘本图片"""
    book_dir = BOOKS_DIR / theme
    return send_from_directory(book_dir, filename)

@app.route('/api/books/<theme>/pdf', methods=['GET'])
def get_book_pdf(theme):
    """获取绘本PDF"""
    book_dir = BOOKS_DIR / theme
    return send_from_directory(book_dir, "book.pdf")

@app.route('/api/books/<theme>', methods=['DELETE'])
def delete_book(theme):
    """删除指定的绘本"""
    try:
        book_dir = BOOKS_DIR / theme

        if not book_dir.exists() or not book_dir.is_dir():
            return jsonify({"success": False, "message": "绘本不存在"}), 404

        # 删除整个目录
        shutil.rmtree(book_dir)

        return jsonify({"success": True, "message": f"已成功删除绘本: {theme}"})

    except Exception as e:
        logger.error(f"删除绘本失败: {str(e)}")
        return jsonify({"success": False, "message": f"删除失败: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)