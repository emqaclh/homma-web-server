from typing import TypedDict, Union
from typeguard import check_type
from flask import Request

from werkzeug import exceptions

from .utils import VALID_ENCODINGS

import os

def validate_request(request: Request) -> None:
  if request.content_type == 'application/json':
    if request.is_json:
      return
  raise exceptions.UnsupportedMediaType('Content type was expected to be application/json')

def validate_request_dict(request: Request) -> None:
  validate_request(request)
  content = request.get_json()
  if type(content) == dict:
    return
  raise exceptions.UnsupportedMediaType('Content was expected to be on dictionary format')

class SessionContentRequestType(TypedDict):
  name: str

def validate_session_content(content: SessionContentRequestType) -> None:
  try:
    check_type('session_content', content, SessionContentRequestType)
  except:
    raise exceptions.BadRequest('Session must have a name <string>.')

class DataFileContentRequestType(TypedDict):
  tag: str
  path: str
  session: str

def validate_datafile_content(content: DataFileContentRequestType) -> None:
  try:
    check_type('datafile_content', content, DataFileContentRequestType)
  except:
    raise exceptions.BadRequest('DataFile must have a tag <string>, path <string> and session <string>.')

  content_folder = os.environ.get('CONTENT_FOLDER', None)
  if not os.path.exists(f'{content_folder}/{content["path"]}'):
    raise exceptions.BadRequest('Declared path file does not exists.')

class DataFileContentEditRequestType(TypedDict):
  tag: str

def validate_datafile_edit(content: DataFileContentEditRequestType) -> None:
  try:
    check_type('datafile_edit', content, DataFileContentEditRequestType)
  except:
    raise exceptions.BadRequest('DataFile should declare a path <string>.')

def validate_datafile_file_upload(request: Request) -> None:
  file = None
  try:
    file = request.files['file']
  except:
    raise exceptions.BadRequest('No file on request body.')
  if not file.content_type == 'text/csv':
    raise exceptions.BadRequest('File content type must be text/csv.')

class DataFileSetupRequestType(TypedDict):
  encoding: str
  sep: str
  decimal: str

def validate_datafile_setup_attempt(content: DataFileSetupRequestType) -> None:
  try:
    check_type('datafile_setup', content, DataFileSetupRequestType)
  except:
    raise exceptions.BadRequest('DataFile setup should declare an encoding <string>, sep <string> and decimal <string>.')

  if content['encoding'] not in VALID_ENCODINGS:
    raise exceptions.BadRequest('Not a valid encoding.')

  if len(content['sep']) > 3:
    raise exceptions.BadRequest('Separator must be contain three or less chars.')

  if len(content['decimal']) > 1:
    raise exceptions.BadRequest('Decimal must be a one-char string.')

def validate_datafile_setup_notify(content: Union[dict, list]) -> None:
  if type(content) == list:
    if all([type(feature) == dict for feature in content]):
      if all(['datatype' in feature and feature['datatype'] in {'numerical', 'non-numerical'} for feature in content]):
        return None
      raise exceptions.BadRequest('Features should declare its name <string> and datatype <string>.')
    raise exceptions.BadRequest('Features must be notified through an array containing the features as maps.')

  elif type(content) == dict:
    if 'error' in content:
      return None
    raise exceptions.BadRequest('Request must contain an error notification.')
  else:
    raise exceptions.BadRequest('Request must contain an array of features or an error.')