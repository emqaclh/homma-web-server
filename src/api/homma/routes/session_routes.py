from http.client import HTTPException
from flask import Blueprint, request, current_app

from .utils.rest_helper import json_response
from ..core.session import Session
from .utils.validation import *

from fakeredis import FakeStrictRedis

import json

session_routes = Blueprint("session", __name__, url_prefix="/session")


@session_routes.route("/a", methods=["GET"])
def test():
    redis = current_app.extensions.get("redis")
    redis.set("a", "b")
    return json_response({"a": redis.get("a").decode("utf-8")}, 200)


@session_routes.route("/", methods=["GET", "POST"])
def session_index():
    if request.method == "GET":
        sessions = Session.objects()
        return json_response([session.to_dict() for session in sessions], 200)

    elif request.method == "POST":
        validate_request_dict(request)
        content = request.get_json()
        validate_session_content(content)
        name = content["name"]
        new_session = Session(name=name)
        new_session.save()
        return json_response(new_session.to_dict(), 201)


@session_routes.route("/<session_id>", methods=["GET", "PATCH", "DELETE"])
def session_element(session_id):
    if request.method == "GET":
        session = Session.objects().get_or_404(pk=session_id)
        return json_response(session.to_dict(), 200)

    elif request.method == "PATCH":
        session = Session.objects().get_or_404(pk=session_id)
        validate_request_dict(request)
        content = request.get_json()
        validate_session_content(content)
        name = content["name"]
        session.set_name(name)
        return json_response({}, 204)

    elif request.method == "DELETE":
        session = Session.objects().get_or_404(pk=session_id)
        session.delete()
        return json_response({}, 200)


@session_routes.route("/<session_id>/datafiles", methods=["GET"])
def session_datafiles(session_id):
    session = Session.objects().get_or_404(pk=session_id)
    return json_response([datafile.to_dict() for datafile in session.datafiles], 200)


@session_routes.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response
