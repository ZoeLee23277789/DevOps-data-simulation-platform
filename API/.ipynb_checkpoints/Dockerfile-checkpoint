FROM python:3.9-slim

WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式程式碼
COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
