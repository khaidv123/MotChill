FROM python:3.10-slim-buster
WORKDIR /MotChill
COPY . /MotChill
RUN apt-get update && apt-get install -y build-essential
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]