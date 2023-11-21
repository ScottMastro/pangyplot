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

        from db.model import link, segment, path, bubble, annotation 
        db.create_all()

        preview_table(link.Link)
        preview_table(segment.Segment)
        preview_table(path.Path)
        preview_table(bubble.Bubble)
        preview_table(bubble.BubbleInside)
        preview_table(annotation.Annotation)

def preview_table(table, n=5):
    tablename = table.__table__.name
    try:
        inspector = db.inspect(db.engine)
        print(f"Table: {tablename}")
        for column in inspector.get_columns(tablename):
            print(f"- {column['name']}: {column['type']}")

        rows = table.query.limit(n).all()
        row_count = table.query.count()
        print("nrows = ", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")
    except:
        print("Failed to print table " + tablename)

def drop(table):

    tablename = table.__table__.name
    connection = db.engine.connect()
    metadata = db.MetaData(bind=db.engine)
    your_table = db.Table(tablename, metadata, autoload=True)
    your_table.drop(connection)
    db.session.commit()
    connection.close()

def drop_all():

    from db.model import link, segment, bubble, path, annotation 

    drop(link.Link)
    drop(segment.Segment)
    drop(path.Path)
    drop(bubble.Bubble)
    drop(bubble.BubbleInside)
    #drop(annotation.Annotation)