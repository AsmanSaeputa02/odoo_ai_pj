{
    'name': 'AI OCR Stock Scanner',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Module สำหรับสแกนเอกสารเข้าสต็อกด้วย AI',
    'depends': ['base', 'stock', 'purchase'],  # เราจะดึงความสามารถของระบบสต็อกมาใช้
    'data': [
        'security/ir.model.access.csv',
        'views/ocr_history_views.xml',
        # เดี๋ยวเราจะเอาไฟล์ XML (หน้าจอ) มาใส่ตรงนี้ในบทถัดไป
    ],
    'installable': True,
    'application': True,
}