FROM python:3.9
WORKDIR /app
RUN pip install gunicorn==20.1.0
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
RUN apt-get update
RUN apt-get install -y locales
RUN locale-gen ru_RU.UTF-8
RUN update-locale
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:7000", "foodgram.wsgi"] 