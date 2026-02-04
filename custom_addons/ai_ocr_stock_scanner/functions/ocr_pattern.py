
# function file
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def extract_thai_id_number(text):
    """
    ดึงเลขบัตรประชาชน 13 หลักจากข้อความ
    
    Args:
        text (str): ข้อความที่ต้องการค้นหา
        
    Returns:
        str or None: เลข 13 หลักที่พบ หรือ None ถ้าไม่พบ
    """
    if not text:
        logger.warning('ข้อความว่างเปล่า ไม่สามารถค้นหาเลขที่ได้')
        return None
    
    # Pattern สำหรับเลข 13 หลัก
    id_pattern = r'\d{13}'
    
    match = re.search(id_pattern, text)
    
    if match:
        id_number = match.group()
        logger.info('ตรวจพบเลขที่: %s', id_number)
        return id_number
    else:
        logger.warning('ไม่พบเลขบัตรประชาชน 13 หลักในข้อความ')
        return None


def extract_date_from_text(text):
    """
    ดึงวันที่จากข้อความและแปลงเป็นรูปแบบ YYYY-MM-DD สำหรับ Odoo
    
    Args:
        text (str): ข้อความที่ต้องการค้นหา
        
    Returns:
        str or None: วันที่รูปแบบ YYYY-MM-DD หรือ None ถ้าไม่พบ
    """
    if not text:
        return None
    
    # Pattern สำหรับวันที่รูปแบบต่างๆ
    date_patterns = [
        (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', 'dmy'),  # 10/05/2565, 15-01-1997
        (r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', 'ymd'),  # 2565-05-10
    ]
    
    for pattern, format_type in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                if format_type == 'dmy':
                    day, month, year = match.groups()
                    # แปลงเป็น Odoo format: YYYY-MM-DD
                    date_obj = datetime(int(year), int(month), int(day))
                    result = date_obj.strftime('%Y-%m-%d')
                    logger.info('ตรวจพบวันที่: %s -> แปลงเป็น %s', match.group(), result)
                    return result
                elif format_type == 'ymd':
                    year, month, day = match.groups()
                    date_obj = datetime(int(year), int(month), int(day))
                    result = date_obj.strftime('%Y-%m-%d')
                    logger.info('ตรวจพบวันที่: %s -> %s', match.group(), result)
                    return result
            except (ValueError, TypeError) as e:
                logger.warning('ไม่สามารถแปลงวันที่ %s: %s', match.group(), e)
                continue
    
    logger.warning('ไม่พบวันที่ในข้อความ')
    return None


def extract_amount_from_text(text):
    """
    ดึงจำนวนเงินจากข้อความ
    
    Args:
        text (str): ข้อความที่ต้องการค้นหา
        
    Returns:
        float or None: จำนวนเงินที่พบ หรือ None ถ้าไม่พบ
    """
    if not text:
        return None
    
    # Pattern สำหรับตัวเลขที่มีจุดหรือคอมม่า
    # เช่น: 1,234.56 หรือ 1234.56
    amount_pattern = r'[\d,]+\.?\d*'
    
    matches = re.findall(amount_pattern, text)
    
    if matches:
        # ลองแปลงตัวแรกที่เป็นตัวเลข
        for match in matches:
            try:
                # ลบคอมม่าออกแล้วแปลงเป็น float
                amount = float(match.replace(',', ''))
                logger.info('ตรวจพบจำนวนเงิน: %.2f', amount)
                return amount
            except ValueError:
                continue
    
    logger.warning('ไม่พบจำนวนเงินในข้อความ')
    return None


def validate_thai_id_number(id_number):
    """
    ตรวจสอบความถูกต้องของเลขบัตรประชาชนไทย (13 หลัก)
    
    Args:
        id_number (str): เลขบัตรประชาชน
        
    Returns:
        bool: True ถ้าถูกต้อง, False ถ้าไม่ถูกต้อง
    """
    if not id_number or len(id_number) != 13:
        return False
    
    if not id_number.isdigit():
        return False
    
    # คำนวณ checksum (algorithm สำหรับเลขบัตรประชาชนไทย)
    total = 0
    for i in range(12):
        total += int(id_number[i]) * (13 - i)
    
    check_digit = (11 - (total % 11)) % 10
    
    return check_digit == int(id_number[12])


def process_ocr_text(raw_text):
    """
    ประมวลผลข้อความจาก OCR ครบวงจร
    
    Args:
        raw_text (str): ข้อความที่ AI อ่านได้
        
    Returns:
        dict: ผลลัพธ์การประมวลผล
            {
                'success': bool,
                'state': str,
                'identified_number': str or None,
                'identified_date': str or None,
                'identified_amount': float or None,
                'error_message': str or None,
            }
    """
    result = {
        'success': False,
        'state': 'error',
        'identified_number': None,
        'identified_date': None,
        'identified_amount': None,
        'error_message': None,
    }
    
    if not raw_text:
        result['error_message'] = 'ไม่พบข้อความจาก AI'
        logger.warning(result['error_message'])
        return result
    
    # ดึงข้อมูลทั้งหมด
    id_number = extract_thai_id_number(raw_text)
    date_str = extract_date_from_text(raw_text)
    amount = extract_amount_from_text(raw_text)
    
    # ตรวจสอบเลขบัตรประชาชน
    if id_number:
        if validate_thai_id_number(id_number):
            result['success'] = True
            result['state'] = 'processed'
            result['identified_number'] = id_number
            logger.info('ประมวลผลสำเร็จ: เลขบัตรประชาชน %s', id_number)
        else:
            result['error_message'] = f'เลขบัตรประชาชนไม่ถูกต้อง: {id_number}'
            logger.warning(result['error_message'])
    else:
        result['error_message'] = 'ไม่พบเลขบัตรประชาชนในข้อความ'
        logger.warning(result['error_message'])
    
    # เก็บข้อมูลเพิ่มเติม (ไม่บังคับ)
    result['identified_date'] = date_str
    result['identified_amount'] = amount
    
    return result


def create_or_update_partner_from_ocr(env, identified_number, scan_date=None):
    if not identified_number:
        return None, 'ไม่พบเลขที่สำหรับดำเนินการ'
    
    # 🔍 1. ค้นหาคู่ค้าเดิม (Search)
    existing_partner = env['res.partner'].search([
        ('ref', '=', identified_number)
    ], limit=1)
    
    partner_vals = {
        'name': f"Partner - {identified_number}",
        'ref': identified_number,
        'comment': f'ข้อมูลล่าสุดจากการสแกน OCR เมื่อ {scan_date}',
    }

    if existing_partner:
        # 📝 2. ถ้าเจอ -> ใช้ .write() เพื่ออัปเดต
        existing_partner.write(partner_vals)
        return existing_partner, 'อัปเดตข้อมูลคู่ค้าเดิมเรียบร้อยแล้ว'
    else:
        # ✨ 3. ถ้าไม่เจอ -> ใช้ .create() เพื่อสร้างใหม่
        new_partner = env['res.partner'].create(partner_vals)
        return new_partner, 'สร้างคู่ค้าใหม่เรียบร้อยแล้ว'