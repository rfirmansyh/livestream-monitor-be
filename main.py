from app.main import init_app

app = init_app()
celery = app.celery_app

# source .venv/bin/activate
# uvicorn main:app --reload

# alembic
# alembic downgrade base
# alembic upgrade head

# celery
# pipenv run celery
# ps aux|grep 'celery worker'
# pkill -f "celery worker"

# redis
# docker exec -it redis sh
# redis-cli

# total_chats_A = 65
# total_chats_B = 78
# total_all_chats = 143

# total_chats_A = 2
# total_chats_B = 2
# total_all_chats = 4

# sql
# SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));


