from  odoo import models,fields,api

class OCRHistory(models.Model):
    _name = 'ocr.history'   # นี่คือชื่อตารางในฐานข้อมูล (จะกลายเป็น ocr_history)
    _description =  'ประวัติการเเสกนเอกสารด้วย AI'

    # ฟิลด์ต่างๆ ที่เราต้องการเก็บ 
    filename = fields.Char(string='ชื่อไฟล์',required=True)
    image_scanned = fields.Binary(string='รูปภาพที่เเสกน')

    # ผลลัพธ์ที่ AI อ่านได้ (เราจะเก็บเป็นข้อความก่อน)
    raw_text = fields.Text(string = 'ข้อความที่ AI อ่านได้')

    # สถานะของการประมวลผล
    state = fields.Selection([
        ('draft' , 'รอดำเนินการ')
        ('processed', 'ประมวลผลสำเร็จ')
        ('error', 'เกิดข้อผิดพลาด')
    ], string='สถานะ', default='draft')

    # ใครเป็นคนทำ? (ความสัมพันธ์แบบ Many2one ไปยังตารางผู้ใช้งาน)
    user_id = fields.Many2one('res.users',string='ผู้ใช้งาน',default=lambda self:self.env.user)
    scan_date = fields.Datetime(string='วันที่เเสกน',default=fields.Datetime.now())




