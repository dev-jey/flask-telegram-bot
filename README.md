# Telegram Bot

This is a chatbot created in flask to enable users to automate the repetitive process of sending messages to channels or groups.

## Installation
1. Clone the repo.

2. Create a virtual environment.

> virtualenv -p python3 env.

3. Install dependecies.
> pip install -r requirements.txt.

4. Export environment variables. 

## Env 

> source env/bin/activate <br>
> export FLASK_ENV=development <br>
> export FLASK_APP=run.py <br>
> export SECRET_KEY=secretkey <br>
> export DATABASE_URL=eg postgres://localhost/telegram <br>
> export APP_SETTINGS=development <br>
> export TIME_MEASURE_SECONDS=60 <br>
> export REDIS_URL=redis://127.0.0.1:6379 <br>
> export MAIL_SERVER=smtp.gmail.com <br>
> export MAIL_PORT=465 <br>
> export MAIL_USERNAME=theadminemail@provider.etc <br>
> export MAIL_PASSWORD=theapppassword <br>
> export MAIL_USE_TLS=False <br>
> export MAIL_USE_SSL=True <br>
<br>

5. Run redis.

> redis-server   

6. Run celery <br>
  
> celery -A  application.celery_worker.celery worker -l info --concurrency=3 --beat -E <br>

7. Start the server <br>
  
> flask run <br>
    
 ## Technologies
Celery.
Selenium
