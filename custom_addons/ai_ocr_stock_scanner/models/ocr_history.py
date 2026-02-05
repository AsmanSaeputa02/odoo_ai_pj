#model file
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _
import re
import base64
import logging
import numpy as np
import cv2
import os
import sys


# Import helper functions จาก functions module
from ..functions import ocr_pattern

logger = logging.getLogger(__name__)

try:
    import easyocr
except ImportError:
    easyocr = None



class OCRHistory(models.Model):
    _name = 'ocr.history'
    _description = 'ประวัติการเเสกนเอกสารด้วย AI'

    filename = fields.Char(string='ชื่อไฟล์', required=True)
    image_scanned = fields.Binary(string='รูปภาพที่เเสกน')
    raw_text = fields.Text(string='ข้อความที่ AI อ่านได้')
    
    state = fields.Selection([
        ('draft', 'รอดำเนินการ'),
        ('processed', 'ประมวลผลสำเร็จ'),
        ('error', 'เกิดข้อผิดพลาด'),
    ], string='สถานะ', default='draft')

    identified_number = fields.Char(string='เลขที่ตรวจพบ')
    identified_date = fields.Date(string='วันที่ตรวจพบ')
    identified_amount = fields.Float(string='ยอดเงินสุทธิ')

    user_id = fields.Many2one('res.users', string='ผู้ใช้งาน', default=lambda self: self.env.user)
    scan_date = fields.Datetime(string='วันที่เเสกน', default=fields.Datetime.now())

    def action_scan_image(self):
        self.ensure_one()

        if not self.image_scanned:
            raise ValidationError("กรุณาอัปโหลดรูปภาพก่อน")
        if not easyocr:
            raise ValidationError("ไม่พบ EasyOCR. กรุณาติดตั้ง EasyOCR ด้วย")

        try:
            # สร้าง EasyOCR Reader สำหรับภาษาไทยและอังกฤษ
            # gpu=False เพื่อใช้ CPU (เหมาะสำหรับ Docker)
            reader = easyocr.Reader(['th', 'en'], gpu=False)
            
            # แปลงรูปภาพจาก base64
            img_data = base64.b64decode(self.image_scanned)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValidationError("ไม่สามารถอ่านรูปภาพได้")
            
            # เรียกใช้ OCR
            # result จะเป็น list ของ [bbox, text, confidence]
            result = reader.readtext(img)

            # ประมวลผลข้อความจาก EasyOCR
            # EasyOCR result format: [[bbox, text, confidence], ...]
            full_text = ""
            if result:
                for detection in result:
                    if len(detection) >= 2:
                        text = detection[1]  # text อยู่ที่ index 1
                        full_text += text + "\n"
            
            if not full_text.strip():
                self.write({'raw_text': 'ไม่พบข้อความ', 'state': 'error'})
                raise ValidationError("OCR ไม่สามารถอ่านข้อความจากรูปภาพได้")
            
            # บันทึกและสกัดข้อมูล
            self.write({'raw_text': full_text})
            
            extraction_result = ocr_pattern.process_ocr_text(self.raw_text)
            
            self.write({
                'identified_number': extraction_result.get('identified_number'),
                'identified_date': extraction_result.get('identified_date'),
                'identified_amount': extraction_result.get('identified_amount'),
                'state': extraction_result.get('state', 'processed')
            })
            
            logger.info("OCR สำเร็จ: %s", self.identified_number)
            return True

        except ValidationError:
            raise
        except Exception as e:
            self.write({'state': 'error'})
            logger.error("OCR Error: %s", str(e), exc_info=True)
            raise UserError(_("PaddleOCR ทำงานผิดพลาด: %s") % str(e))


    def action_create_partner(self):
        self.ensure_one()
        
        partner, message = ocr_pattern.create_or_update_partner_from_ocr(
            self.env, 
            self.identified_number, 
            self.scan_date
        )
        
        if not partner:
            raise ValidationError(message)
        
        self.write({'state': 'processed'})
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': partner.id,
            'view_mode': 'form',
            'target': 'current',
        }