# ใช้ Odoo 17.0 เป็น base image
FROM odoo:17.0

# Switch to root เพื่อติดตั้ง packages
USER root

# ติดตั้ง dependencies ที่จำเป็นสำหรับ PaddleOCR, OpenCV และ Python packages
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, และ wheel ก่อน
RUN pip3 install --upgrade pip setuptools wheel

# Copy requirements.txt
COPY requirements.txt /tmp/requirements.txt

# ติดตั้ง Python packages จาก requirements.txt
# ใช้ --no-cache-dir เพื่อลดขนาด image และป้องกัน cache conflicts
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Clean up
RUN rm /tmp/requirements.txt

# Switch กลับเป็น odoo user
USER odoo
