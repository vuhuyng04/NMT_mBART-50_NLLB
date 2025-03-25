# Sử dụng Python chính thức làm image base
FROM python:3.9-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Cài đặt các gói hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Sao chép file requirements.txt vào container
COPY requirements.txt .  

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt  

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Mở cổng 80 để có thể truy cập từ bên ngoài mà không cần ghi port
EXPOSE 80  

# Định nghĩa biến môi trường
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV HOST=0.0.0.0
ENV PORT=80  # Đổi port 5000 -> 80 để truy cập không cần ghi cổng

# Cài đặt Gunicorn để chạy ứng dụng Flask
RUN pip install gunicorn

# Chạy ứng dụng Flask bằng Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "3", "app:app"]
