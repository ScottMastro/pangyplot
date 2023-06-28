import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

db = SQLAlchemy()

def db_config():
    load_dotenv()

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"