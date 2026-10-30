FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHROME_BIN=/opt/chrome/chrome-linux64/chrome \
    CHROMEDRIVER=/usr/local/bin/chromedriver \
    REGISTRATION=FA23-BDS-024

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libglib2.0-0 \
    libgtk-3-0 libnspr4 libnss3 libx11-6 libxcomposite1 libxdamage1 \
    libxext6 libxfixes3 libxkbcommon0 libxrandr2 libxss1 libxtst6 \
    wget xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY install_chrome.py /app/
RUN python install_chrome.py \
    && /opt/chrome/chrome-linux64/chrome --version \
    && /usr/local/bin/chromedriver --version

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py news_sources.py scraper.py summarizer.py /app/

EXPOSE 7000
CMD ["gunicorn", "--bind", "0.0.0.0:7000", "--workers", "1", "--threads", "2", "--timeout", "90", "app:app"]
