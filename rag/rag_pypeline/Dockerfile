FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev build-essential tesseract-ocr \
    libtesseract-dev poppler-utils libreoffice pandoc libgl1-mesa-glx \
    libglib2.0-0 curl git && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip3 install --no-cache-dir --upgrade pip

COPY src/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY src/ /app/src/

EXPOSE 8000
CMD ["python3", "/app/src/main.py"]
