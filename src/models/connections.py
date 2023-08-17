import datetime
import sqlalchemy as sql
from src import db


class DeviceConnection(db.Model):
    __tablename__ = "device_connection"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    device_id = sql.Column(sql.Integer, sql.ForeignKey("device.id"))
    duration = sql.Column(sql.Float)
    state = sql.Column(sql.Boolean)
    created_at = sql.Column(sql.DateTime, nullable=False)

    def __init__(self, device_id: int, duration: int, state: bool):
        self.device_id = device_id
        self.duration = duration
        self.state = state
        self.created_at = datetime.datetime.utcnow()
