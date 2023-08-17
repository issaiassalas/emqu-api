from flask import jsonify, Blueprint, request
from src import db
from src.utils import is_device_owner, login_required
from src.models import User, Device, DeviceConnection

execution_blueprint = Blueprint("execution", __name__)


@execution_blueprint.route("/ping/device/<int:ip_id>", methods=["POST"])
@is_device_owner
def ping_ip(user: User, device: Device):
    status, time = device.ping_address()
    connection = DeviceConnection(device.id, time, status)
    db.session.add(connection)
    db.session.commit()
    return (
        jsonify(
            {
                "data": {"id": connection.id, "status": status, "time": time},
                "status": "success",
            }
        ),
        200,
    )


@execution_blueprint.route("/device/<int:ip_id>/stats")
@is_device_owner
def device_stats(user: User, device: Device):
    return jsonify(device.get_stats())


@execution_blueprint.route("/user/stats")
@login_required
def user_stats(user: User):
    count_of_devices = len(user.devices)
    devices_order_by_date = sorted(
        filter(lambda x: bool(x.last_request_at), user.devices),
        key=lambda x: x.last_request_at,
    )
    last_request_at = devices_order_by_date[0] if devices_order_by_date else None
    first_request_at = devices_order_by_date[-1] if devices_order_by_date else None
    unused_devices_count = count_of_devices - len(devices_order_by_date)

    return jsonify(
        {
            "count_of_devices": count_of_devices,
            "first_requested_device": first_request_at.get_json(),
            "last_requested_device": last_request_at.get_json(),
            "unused_devices_count": unused_devices_count,
        }
    )
