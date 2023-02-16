import os
from app.enums import DataSource, ThresholdMode, ProtocolType, Order


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database2.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'migrations')
    DATA_SOURCE = DataSource.Device
    DATA_FILE = 'data-48.txt'
    DATA_PORT = "COM7"
    BAUD_RATE = 921600
    THRESHOLD_MIN = 50000
    THRESHOLD_MAX = 100000
    THRESHOLD_MODE = ThresholdMode.Dynamic
    PROTOCOL_MODE = ProtocolType.New
    EYE_ORDER = Order.RightLeft
    LEFT_THRESHOLD_COEFF = 1.5

