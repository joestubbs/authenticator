import datetime
import enum
from flask import Flask, g
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from hashids import Hashids
import uuid

from common.config import conf
from common.errors import DAOError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = conf.sql_db_url
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# get the logger instance -
from common.logs import get_logger
logger = get_logger(__name__)


class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(80), unique=True, nullable=False)
    client_key = db.Column(db.String(80), unique=False, nullable=False)
    tenant_id = db.Column(db.String(50), unique=False, nullable=False)
    username = db.Column(db.String(50), unique=False, nullable=False)
    callback_url = db.Column(db.String(200), unique=False, nullable=True)
    create_time = db.Column(db.DateTime, nullable=False)
    last_update_time = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    HASH_SALT = 'hQb9xTr7j8vSu'

    def __repr__(self):
        return f'{self.client_id}'

    @property
    def serialize(self):
        return {
            "client_id": self.client_id,
            "client_key": self.client_key,
            "owner": self.username,
            "callback_url": self.callback_url,
            "create_time": self.create_time,
            "last_update_time": self.last_update_time
        }

    @classmethod
    def generate_client_id(cls):
        """
        Generates a client_id when none is provided by the user.
        :return: 
        """
        hashids = Hashids(salt=Client.HASH_SALT)
        return hashids.encode(uuid.uuid1().int>>64)

    @classmethod
    def get_derived_values(cls, data):
        """
        Computes derived values for the client from input and defaults.
        :param data:
        :return: dict (result)
        """
        result = {}
        result['tenant_id'] = g.tenant_id
        result['username'] = g.username
        result['create_time'] = datetime.datetime.utcnow()
        result['last_update_time'] = datetime.datetime.utcnow()
        # client_id and client_key are optional fields -- if they are not passed, the service will generate them.
        try:
            result['client_id'] = getattr(data, 'client_id')
        except AttributeError:
            result['client_id'] = Client.generate_client_id()
        try:
            result['client_key'] = getattr(data, 'client_key')
        except AttributeError:
            result['client_key'] = Client.generate_client_id()
        try:
            result['callback_url'] = getattr(data, 'callback_url')
        except AttributeError:
            result['callback_url'] = ''
        return result


class AuthorizationCode(db.Model):
    __tablename__ = 'authorization_codes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    tenant_id = db.Column(db.String(50), unique=False, nullable=False)
    client_id = db.Column(db.String(80), db.ForeignKey('clients.client_id'), unique=True, nullable=False)
    client_key = db.Column(db.String(80), unique=False, nullable=False)
    redirect_url = db.Column(db.String(200), unique=False, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    expiry_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'{self.code}'

    @property
    def serialize(self):
        return {
            "code": self.code,
            "expiry_time": self.expiry_time
        }
