from flask import Blueprint, request, jsonify
from src import bcrypt, db
from src.models import User, BlacklistToken
from src.utils import login_required

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/register", methods=["POST"])
def register():
    # get the post data
    post_data = request.get_json()
    # check if user already exists
    user = User.query.filter_by(email=post_data.get("email")).first()
    if not user:
        try:
            user = User(
                email=post_data.get("email"), password=post_data.get("password")
            )
            # insert the user
            db.session.add(user)
            db.session.commit()
            # generate the auth token
            auth_token = user.encode_auth_token(user.id)
            responseObject = {
                "status": "success",
                "message": "Successfully registered.",
                "auth_token": auth_token,
            }
            return jsonify(responseObject), 201
        except Exception as e:
            responseObject = {
                "status": "fail",
                "message": "Some error occurred. Please try again.",
            }
            return jsonify(responseObject), 401
    else:
        responseObject = {
            "status": "fail",
            "message": "User already exists. Please Log in.",
        }
        return jsonify(responseObject), 202


@auth_blueprint.route("/login", methods=["POST"])
def login():
    # get the post data
    post_data = request.get_json()
    try:
        # fetch the user data
        user = User.query.filter_by(email=post_data.get("email")).first()
        if user and bcrypt.check_password_hash(
            user.password, post_data.get("password")
        ):
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                responseObject = {
                    "status": "success",
                    "message": "Successfully logged in.",
                    "auth_token": auth_token,
                }
                return jsonify(responseObject), 200
        else:
            responseObject = {"status": "fail", "message": "User does not exist."}
            return jsonify(responseObject), 404
    except Exception as e:
        print(e)
        responseObject = {"status": "fail", "message": "Try again"}
        return jsonify(responseObject), 500


@auth_blueprint.route("/me", methods=["GET"])
@login_required
def me(user: User):
    responseObject = {
        "status": "success",
        "data": {
            "user_id": user.id,
            "email": user.email,
            "admin": user.admin,
            "registered_on": user.registered_on,
        },
    }
    return jsonify(responseObject), 200


@auth_blueprint.route("/logout", methods=["POST"])
@login_required
def logout(user: User):
    # get auth token
    auth_header = request.headers.get("Authorization")
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ""
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            # mark the token as blacklisted
            blacklist_token = BlacklistToken(token=auth_token)
            try:
                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()
                responseObject = {
                    "status": "success",
                    "message": "Successfully logged out.",
                }
                return jsonify(responseObject), 200
            except Exception as e:
                responseObject = {"status": "fail", "message": e}
                return jsonify(responseObject), 200
        else:
            responseObject = {"status": "fail", "message": resp}
            return jsonify(responseObject), 401
    else:
        responseObject = {"status": "fail", "message": "Provide a valid auth token."}
        return jsonify(responseObject), 403
