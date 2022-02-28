from http.client import HTTPException
from flask import Blueprint, request
from werkzeug import exceptions

from ..core.session import Session
from ..core.datafile import DataFile
from ..core.feature import Feature
from .utils.rest_helper import json_response
from .utils.validation import *

import uuid
import json
import os

content_folder = os.environ.get("CONTENT_FOLDER", None)

datafile_routes = Blueprint("datafile", __name__, url_prefix="/datafile")


@datafile_routes.route("/", methods=["POST"])
def datafile_index():
    validate_request_dict(request)
    content = request.get_json()
    validate_datafile_content(content)
    session = Session.objects().get_or_404(pk=content["session"])
    new_datafile = DataFile(tag=content["tag"], path=content["path"])
    new_datafile.save()
    session.datafiles.append(new_datafile)
    session.save()
    return json_response(new_datafile.to_dict(), 201)


@datafile_routes.route("/<datafile_id>", methods=["GET", "PATCH", "DELETE"])
def datafile_element(datafile_id):
    if request.method == "GET":
        datafile = DataFile.objects().get_or_404(pk=datafile_id)
        return json_response(datafile.to_dict(), 200)

    elif request.method == "PATCH":
        datafile = DataFile.objects().get_or_404(pk=datafile_id)
        validate_request_dict(request)
        content = request.get_json()
        validate_datafile_edit(content)
        tag = content["tag"]
        datafile.set_tag(tag)
        return json_response({}, 204)

    elif request.method == "DELETE":
        datafile = DataFile.objects().get_or_404(pk=datafile_id)
        datafile.delete()
        return json_response({}, 200)


@datafile_routes.route("/<datafile_id>/setup_attempt", methods=["POST"])
def attempt_setup(datafile_id):
    datafile = DataFile.objects().get_or_404(pk=datafile_id)
    if datafile.consolidated:
        raise exceptions.BadRequest("DataFile is already consolidated.")
    validate_request_dict(request)
    content = request.get_json()
    validate_datafile_setup_attempt(content)
    datafile.set_setup(content)
    datafile.reset_setup_key()
    """
  ATTEMPT SETUP LOGIC
  """
    return json_response({}, 201)


@datafile_routes.route("/<datafile_id>/setup_notify", methods=["POST"])
def notify_setup(datafile_id):
    validate_request(request)
    datafile = DataFile.objects().get_or_404(pk=datafile_id)
    if datafile.consolidated:
        raise exceptions.BadRequest("DataFile is already consolidated.")
    content = request.get_json()
    validate_datafile_setup_notify(content)
    if type(content) == list:
        datafile.set_features(content)
    else:
        datafile.clear_features()
    return json_response({}, 201)


@datafile_routes.route("/<datafile_id>/features", methods=["GET"])
def datafile_features(datafile_id):
    datafile = DataFile.objects().get_or_404(pk=datafile_id)
    return json_response([feature.to_dict() for feature in datafile.features], 200)


@datafile_routes.route("/<datafile_id>/consolidate_request", methods=["POST"])
def datafile_consolidate_request(datafile_id):
    datafile = DataFile.objects().get_or_404(pk=datafile_id)
    if datafile.consolidated or len(datafile.features) < 1:
        raise exceptions.PreconditionFailed(
            "DataFile is already consolidated or there is no features."
        )
    """
  CONSOLIDATION LOGIC
  """
    return json_response({}, 201)


@datafile_routes.route("/<datafile_id>/consolidate_notify", methods=["POST"])
def datafile_consolidate_notify(datafile_id):
    datafile = DataFile.objects().get_or_404(pk=datafile_id)
    if datafile.consolidated or len(datafile.features) < 1:
        raise exceptions.PreconditionFailed(
            "DataFile is already consolidated or there is no features."
        )
    datafile.consolidated = True
    datafile.save()
    return json_response({}, 201)


@datafile_routes.route("/upload", methods=["POST"])
def upload_file():
    validate_datafile_file_upload(request)
    file = request.files["file"]
    content_folder = os.environ.get("CONTENT_FOLDER", None)
    new_path = f"{uuid.uuid4().hex}.csv"
    file.save(f"{content_folder}/{new_path}")
    return json_response({"path": new_path}, 201)


@datafile_routes.errorhandler(HTTPException)
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
