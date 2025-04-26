FROM python:latest

WORKDIR /PMS

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /PMS/PMS

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0:8080"]