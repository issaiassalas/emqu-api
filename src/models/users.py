import datetime
import sqlalchemy as sql
import jwt
from src import db, bcrypt, app


class User(db.Model):
    """User Model for storing user related details"""

    __tablename__ = "users"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    email = sql.Column(sql.String(255), unique=True, nullable=False)
    password = sql.Column(sql.String(255), nullable=False)
    registered_on = sql.Column(sql.DateTime, nullable=False)
    admin = sql.Column(sql.Boolean, nullable=False, default=False)

    devices = db.relationship("Device", backref="users")

    def __init__(self, email: str, password: str, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode()
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def encode_auth_token(self, user_id: int):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=3),
                "iat": datetime.datetime.utcnow(),
                "sub": user_id,
            }
            return jwt.encode(payload, app.config.get("SECRET_KEY"), algorithm="HS256")
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token: str):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(
                auth_token, app.config.get("SECRET_KEY"), algorithms=["HS256"]
            )
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return "Token blacklisted. Please log in again."
            else:
                return payload["sub"]
        except jwt.ExpiredSignatureError:
            return "Signature expired. Please log in again."
        except jwt.InvalidTokenError:
            return "Invalid token. Please log in again."

    def get_ip_addresses(self):
        return [ip.get_json() for ip in self.ip_addresses]


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """

    __tablename__ = "blacklist_token"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    token = sql.Column(sql.String(500), unique=True, nullable=False)
    blacklisted_on = sql.Column(sql.DateTime, nullable=False)

    def __init__(self, token: str):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return "<id: token: {}".format(self.token)

    @staticmethod
    def check_blacklist(auth_token: str):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False
