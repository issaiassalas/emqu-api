import jwt

from flask import request, jsonify
from functools import wraps

from src.models import User, Device


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = None
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    "status": "fail",
                    "message": "Bearer token malformed.",
                }
                return jsonify(responseObject), 401
        else:
            auth_token = ""
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
        if not user:
            responseObject = {
                "status": "fail",
                "message": "Provide a valid auth token.",
            }
            return jsonify(responseObject), 401
        return f(user, *args, **kwargs)

    return decorated_function


def is_device_owner(f):
    @wraps(f)
    @login_required
    def decorated_function(user: User, ip_id: int, *args, **kwargs):
        device = Device.query.filter_by(id=ip_id).first()
        if device:
            if device.user_id == user.id:
                return f(user, device, *args, **kwargs)
            return jsonify({"message": "not allowed", "status": "error"}), 403
        return jsonify({"message": "not found", "status": "error"}), 404

    return decorated_function
