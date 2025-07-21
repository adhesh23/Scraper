FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip fonts-liberation libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 \
    libnspr4 libnss3 libxcomposite1 libxdamage1 libxrandr2 \
    libxss1 libxtst6 xdg-utils libgbm1 libgtk-3-0 \
    libxshmfence1 libglu1-mesa libx11-xcb1 libxext6 \
    libgles2 bash \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Playwright and Chromium
RUN pip install playwright
RUN playwright install chromium

# Copy application code
COPY . .

# Run Flask app
CMD ["python", "main.py"]
