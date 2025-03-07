# generators/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def create_pdf(pages, style):
    c = canvas.Canvas("output/storybook.pdf", pagesize=A4)

    for i, (text, img_path) in enumerate(pages):
        # 添加图片
        img = ImageReader(img_path)
        c.drawImage(img, 50, 400, width=500, height=300)

        # 添加文字
        font_size = 14
        while c.stringWidth(text, "Helvetica", font_size) > 450:
            font_size -= 1
        c.setFont("Helvetica", font_size)

        text_object = c.beginText(50, 380)
        text_object.textLines(text)
        c.drawText(text_object)

        c.showPage()

    c.save()
