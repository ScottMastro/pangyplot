import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

db = SQLAlchemy()

def db_init(app):
    load_dotenv()

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    db.init_app(app)

    with app.app_context():

        from data.model import link, segment, bubble, annotation 
        db.create_all()

        preview_table(db, link.Link)
        preview_table(db, segment.Segment)
        preview_table(db, bubble.Bubble)
        preview_table(db, bubble.BubbleInside)
        preview_table(db, annotation.Annotation)

def preview_table(db, table, n=5):

    inspector = db.inspect(db.engine)
    print(f"Table: {table.__table__.name}")
    for column in inspector.get_columns(table.__table__.name):
        print(f"- {column['name']}: {column['type']}")

    rows = table.query.limit(n).all()
    row_count = table.query.count()
    print("nrows = ", row_count)
    print("--------")
    for row in rows:
        print(row)
    print("--------")
