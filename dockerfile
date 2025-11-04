# ✅ ใช้ base image ที่เป็น Python 3.9
FROM python:3.9-bullseye

# ✅ ติดตั้ง Java (สำหรับ Spark), curl (โหลดไฟล์), git (สำหรับ clone หรือ poetry อาจใช้)
RUN pip install -U pip\
    && apt-get update\
    && apt-get install -y \
    openjdk-11-jdk \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ✅ ติดตั้ง Poetry เวอร์ชัน 1.8.2 สำหรับจัดการ dependencies
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# ✅ ตั้งโฟลเดอร์ทำงานเป็น /app
WORKDIR /app

# ✅ คัดลอกไฟล์สำหรับpoetryจากโปรเจกต์ไปยัง container
COPY  poetry.lock pyproject.toml /app/

# ✅ บอก Poetry ว่าให้ติดตั้ง package ลงระบบตรง ๆ (ไม่สร้าง virtualenv แยก)
# ✅ แล้วติดตั้ง dependencies จาก pyproject.toml
RUN poetry config virtualenvs.create false \
 && poetry install

# ✅ คัดลอกไฟล์ทั้งหมดจากโปรเจกต์ไปยัง container
COPY  ./ /app/

# ✅ ดาวน์โหลด PostgreSQL JDBC Driver (ใช้สำหรับ Spark เชื่อมกับ PostgreSQL)
RUN curl -o /app/postgresql-42.6.0.jar https://jdbc.postgresql.org/download/postgresql-42.6.0.jar

# ✅ ตั้งคำสั่งเริ่มต้นเมื่อ container รัน: รันไฟล์ main.py
CMD ["poetry","run","python", "main.py", \
    "--source","/opt/data/transaction.csv", \
    "--database","warehouse", \
    "--table","customers"]
