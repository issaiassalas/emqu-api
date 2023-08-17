from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from src import db
from src.models import Device, User
from src.utils import login_required, is_device_owner

device_blueprint = Blueprint("device", __name__)


@device_blueprint.route("/device", methods=["GET"])
@login_required
def index(user: User):
    devices = Device.query.filter_by(user_id=user.id).all()
    return (
        jsonify(
            {"data": [device.get_json() for device in devices], "status": "success"}
        ),
        200,
    )


@device_blueprint.route("/device", methods=["POST"])
@login_required
def create(user: User):
    data = request.get_json()
    try:
        result = Device.DeviceSchema().load(data)
    except ValidationError as e:
        return (
            jsonify(
                {
                    "message": "argument error",
                    "messages": e.messages,
                    "status": "error",
                }
            ),
            400,
        )
    if Device.validate_ip(data.get("ip_address")):
        try:
            device = Device(data.get("name"), data.get("ip_address"), user.id)
            db.session.add(device)
            db.session.commit()
            return jsonify(
                {
                    "data": {
                        "id": device.id,
                        "name": device.name,
                        "ip_address": device.ip_address,
                    },
                    "status": "success",
                }
            )
        except Exception as e:
            return (
                jsonify(
                    {
                        "message": str(e),
                        "status": "error",
                    }
                ),
                400,
            )
    return (
        jsonify({"message": "not a valid ip provided", "status": "error"}),
        400,
    )


@device_blueprint.route("/device/<int:ip_id>")
@is_device_owner
def get(user: User, device: Device):
    return jsonify({"data": device.get_json(), "status": "success"}), 200


@device_blueprint.route("/device/<int:ip_id>", methods=["PUT"])
@is_device_owner
def update(user: User, device: Device):
    data = request.get_json()
    if data.get("name"):
        device.name = data.get("name")
        db.session.commit()
    return jsonify({"data": device.get_json(), "status": "success"}), 200


@device_blueprint.route("/device/<int:ip_id>", methods=["DELETE"])
@is_device_owner
def delete(user: User, device: Device):
    if len(device.connections) == 0:
        id = device.id
        db.session.delete(device)
        db.session.commit()
        return jsonify({"data": {"id": id}, "status": "success"}), 200
    return jsonify({"message": "not allowed to delete used ip"}), 403
