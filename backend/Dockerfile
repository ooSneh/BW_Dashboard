FROM selenium/standalone-chrome

USER root

RUN apt-get update && apt-get install -y python3-pip

WORKDIR /app

COPY backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install lxml

COPY backend/WebScraper.py .

CMD ["python3", "WebScraper.py"]