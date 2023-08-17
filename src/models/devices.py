import ipaddress
import subprocess
import datetime
import sqlalchemy as sql
from flask_marshmallow import Schema
from marshmallow import fields

from src import db


class Device(db.Model):
    """IP config model"""

    __tablename__ = "device"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    name = sql.Column(sql.String(255), nullable=False)
    ip_address = sql.Column(sql.String(255), unique=True, nullable=False)
    created_at = sql.Column(sql.DateTime, nullable=False)
    last_request_at = sql.Column(sql.DateTime)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"))

    connections = db.relationship("DeviceConnection", backref="device")

    def __init__(self, name: str, ip: str, user_id: int) -> None:
        self.name = name
        self.ip_address = ip
        self.user_id = user_id
        self.created_at = datetime.datetime.utcnow()

    def get_stats(self):
        request_count = len(self.connections)
        success_con = [con.duration for con in self.connections if con.state]
        success_count = len(success_con)
        failed_count = request_count - success_count
        max_time = max(success_con) if success_con else 0
        min_time = min(success_con) if success_con else 0
        mean_time = (sum(success_con) / len(success_con)) if success_con else 0
        sorted_by_date = sorted(self.connections, key=lambda x: x.created_at)
        first_time_requested = sorted_by_date[0] if sorted_by_date else None
        last_time_requested = sorted_by_date[-1] if sorted_by_date else None
        return {
            "request_count": request_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "max_time_waited": max_time,
            "min_time_waited": min_time,
            "mean_time": mean_time,
            "first_time_requested": first_time_requested.created_at,
            "last_time_requested": last_time_requested.created_at,
        }

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "ip_address": self.ip_address,
            "created_at": self.created_at,
            "last_request_at": self.last_request_at,
        }

    @staticmethod
    def validate_ip(ip: str) -> bool:
        try:
            return bool(ipaddress.ip_address(ip))
        except ValueError:
            return False

    def ping_address(self):
        try:
            # Run the ping command and redirect the output to the subprocess.PIPE object
            process = subprocess.Popen(
                ["ping", "-n", "4", self.ip_address],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Get the output of the ping command and decode it
            output, error = process.communicate()
            output = output.decode("utf-8")

            # Extract the status, time, received packets, and number of packets from the output
            status = "Active" if "time=" in output else "Inactive"
            time = None

            if status == "Active":
                time_start = output.find("time=")
                time_end = output.find("ms", time_start)
                time = output[time_start + 5 : time_end].strip()

            time = 0 if not time else int(time)
            self.last_request_at = datetime.datetime.utcnow()
            return status == "Active", time

        except Exception as e:
            print("Error while pinging:", str(e))

    class DeviceSchema(Schema):
        name = fields.String(required=True)
        ip_address = fields.String(required=True)
