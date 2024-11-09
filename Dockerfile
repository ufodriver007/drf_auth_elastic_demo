FROM python:3.12

RUN pip install --upgrade pip
RUN apt update -y

WORKDIR /ufo

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD python manage.py makemigrations \
        && python manage.py migrate \
        && python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='root').exists() or User.objects.create_superuser('root', 'root@example.com', 'root')" \
        && gunicorn drf_downloader.wsgi:application --bind 0.0.0.0:8000 --log-level info
