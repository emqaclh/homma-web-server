from flask import make_response, Response, jsonify

def json_response(response: dict, http_code: int) -> Response:
  return make_response(jsonify(response), http_code)