# 🐛 Odoo Remote Debug Guide

## วิธีการ Debug Odoo แบบเห็นการทำงานจริง

### 📋 สิ่งที่ต้องเตรียม:
✅ Docker ตั้งค่าเรียบร้อยแล้ว (มี debugpy port 5678)
✅ VSCode มี Python extension
✅ launch.json ตั้งค่าแล้ว

---

## 🚀 ขั้นตอนการ Debug:

### 1️⃣ Restart Docker with Debug Mode
```bash
cd c:\Users\asman_s\Downloads\my-odoo-ai-project
docker-compose down
docker-compose up -d
```

รอประมาณ 30-60 วินาที ให้ Odoo start เสร็จ

### 2️⃣ เปิด Odoo ใน Browser
```
http://localhost:8069
```

### 3️⃣ วาง Breakpoint ใน VSCode
เปิดไฟล์: `custom_addons/ai_ocr_stock_scanner/models/ocr_history.py`

วาง breakpoint ที่:
```python
def action_scan_image(self):
    self.ensure_one()
    
    # เรียกใช้ function ประมวลผล
    result = ocr_pattern.process_ocr_text(self.raw_text)  # ← วาง breakpoint ตรงนี้!
```

**วิธีวาง breakpoint:**
- คลิกที่ซ้ายสุดของบรรทัด (จุดสีแดงจะปรากฏ)
- หรือกด `F9` ที่บรรทัดนั้น

### 4️⃣ Attach Debugger
ใน VSCode:
1. กด `Ctrl+Shift+D` (เปิด Debug panel)
2. เลือก **"🐳 Docker: Attach to Odoo"** จาก dropdown
3. กด **F5** หรือคลิก ▶️ สีเขียว
4. รอจนขึ้นข้อความ **"Attached to debugpy"** ใน Debug Console

### 5️⃣ ทดสอบใน Odoo
1. ใน Odoo ไปที่: **AI Scanner → History**
2. **Create** record ใหม่
3. กรอก **Filename** และใส่ **ผลลัพธ์จาก AI** (raw_text)
4. **Save** (💾)
5. กดปุ่ม **"เริ่มสแกนด้วย AI"** 🔍

### 6️⃣ Debug!
เมื่อกดปุ่ม → **VSCode จะหยุดที่ breakpoint!** 🎉

ตอนนี้คุณสามารถ:
- ✅ ดูค่าตัวแปร (hover mouse)
- ✅ Step Over (F10)
- ✅ Step Into (F11)
- ✅ Continue (F5)
- ✅ ดู call stack
- ✅ ดู variables panel

---

## 🎯 Tips:

### วาง Breakpoint ที่ไหนดี?

| ไฟล์ | บรรทัดที่แนะนำ | เพื่อดู |
|------|----------------|---------|
| `models/ocr_history.py` | `action_scan_image()` | การเรียกใช้ function |
| `models/ocr_history.py` | `action_create_partner()` | การสร้าง Partner |
| `functions/ocr_pattern.py` | `process_ocr_text()` | การประมวลผล |
| `functions/ocr_pattern.py` | `extract_thai_id_number()` | การดึงเลขบัตร |

### Keyboard Shortcuts:

| ปุ่ม | คำสั่ง |
|------|--------|
| `F5` | Continue / Start Debug |
| `F9` | Toggle Breakpoint |
| `F10` | Step Over (ข้ามไป) |
| `F11` | Step Into (เข้าไปใน function) |
| `Shift+F11` | Step Out (ออกจาก function) |
| `Shift+F5` | Stop Debug |

### ดู Variables:

ใน Debug panel ด้านซ้าย จะมีส่วน:
- **Variables** = ตัวแปรทั้งหมด
- **Watch** = ตัวแปรที่เฝ้าดู
- **Call Stack** = function ที่เรียกมา

---

## ⚠️ Troubleshooting:

### ❌ "Failed to attach" 
**สาเหตุ:** Odoo ยังไม่ start เสร็จ
**วิธีแก้:** รอ 1-2 นาที แล้วลอง attach อีกครั้ง

### ❌ Breakpoint ไม่หยุด
**สาเหตุ:** Path mapping ผิด
**วิธีแก้:** ตรวจสอบว่า `pathMappings` ใน launch.json ถูกต้อง

### ❌ "Connection refused"
**สาเหตุ:** Port 5678 ไม่เปิด
**วิธีแก้:** 
```bash
docker-compose down
docker-compose up -d
docker-compose logs web | grep debugpy
```

---

## 🎉 สรุป:

1. ✅ Restart Docker
2. ✅ วาง Breakpoint
3. ✅ Attach Debugger (F5)
4. ✅ กดปุ่มใน Odoo
5. ✅ Debug!

ขอให้สนุกกับการ debug! 🚀
