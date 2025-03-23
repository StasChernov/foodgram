FROM python:3.9
WORKDIR /app
RUN pip install gunicorn==20.1.0
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
RUN apt-get clean && apt-get update && apt-get install -y locales-all
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:7000", "foodgram.wsgi"] 