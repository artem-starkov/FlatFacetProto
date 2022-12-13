import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app/database.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
