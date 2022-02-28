import pytest
import json

from werkzeug.datastructures import FileStorage

@pytest.fixture(scope='session')
def session_id(test_client):
  response = test_client.post('/session/', data=json.dumps(dict(name='test_session_functions')), content_type='application/json')
  return response.json['unique_id']

def test_api_datafile_upload_empty_payload_content(test_client):

  response = test_client.post('/datafile/upload', data=dict(), content_type='multipart/form-data')
  assert response.status_code == 400

def test_api_datafile_upload_wrong_content_type(test_client):

  response = test_client.post('/datafile/upload', data=json.dumps(dict()), content_type='application/json')
  assert response.status_code == 400

def test_api_datafile_upload(temp_csv, test_client):

  file = FileStorage(
    stream=open(temp_csv, 'rb'),
    filename='test.csv',
    content_type='text/csv'
  )
  response = test_client.post('/datafile/upload', data=dict(file=file), content_type='multipart/form-data')
  assert response.status_code == 201
  assert 'path' in response.json
  print(response.json['path'])

@pytest.fixture(scope='session')
def file_path(temp_csv, test_client):
  file = FileStorage(
    stream=open(temp_csv, 'rb'),
    filename='test.csv',
    content_type='text/csv'
  )
  response = test_client.post('/datafile/upload', data=dict(file=file), content_type='multipart/form-data')
  file_path = response.json['path']
  return file_path

def test_api_datafile_post_nonexistent_file(test_client):

  response = test_client.post('/datafile/', data=json.dumps(dict(tag='df_test', path='non_existent.csv')), content_type='application/json')
  assert response.status_code == 400

def test_api_datafile_post(test_client, file_path, session_id):

  response = test_client.post('/datafile/', data=json.dumps(dict(tag='df_test', path=file_path, session=session_id)), content_type='application/json')
  assert response.status_code == 201
  assert 'tag' in response.json
  assert response.json['tag'] == 'df_test'

def test_api_datafile_retrieve_from_session(test_client, session_id, file_path):
  
  test_client.post('/datafile/', data=json.dumps(dict(tag='df_test', path=file_path, session=session_id)), content_type='application/json')
  response = test_client.get(f'/session/{session_id}/datafiles')
  assert response.status_code == 200
  data = response.json
  assert len(data) > 0

@pytest.fixture(scope='session')
def datafile_id(test_client, session_id, file_path):

  response = test_client.post('/datafile/', data=json.dumps(dict(tag='df_test', path=file_path, session=session_id)), content_type='application/json')
  return response.json['unique_id']

def test_api_datafile_get(test_client, datafile_id):
  
  response = test_client.get(f'datafile/{datafile_id}')
  assert response.status_code == 200
  data = response.json
  assert data['tag'] == 'df_test'

def test_api_datafile_patch(test_client, datafile_id):

  response = test_client.patch(f'datafile/{datafile_id}', data=json.dumps(dict(tag='new_tag')), content_type='application/json')
  assert response.status_code == 204

  response = test_client.get(f'datafile/{datafile_id}')
  assert response.status_code == 200
  data = response.json
  assert data['tag'] == 'new_tag'

def test_api_datafile_attempt_setup(test_client, datafile_id):

  response = test_client.post(f'datafile/{datafile_id}/setup_attempt', data=json.dumps(dict(sep=';', decimal='.', encoding='latin-1')), content_type='application/json')
  assert response.status_code == 201

  response = test_client.get(f'datafile/{datafile_id}')
  assert response.status_code == 200
  data = response.json
  setup = data['setup']
  assert setup['encoding'] == 'latin-1'
  assert setup['sep'] == ';'
  assert setup['decimal'] == '.'

def test_api_datafile_notify_setup(test_client, datafile_id):

  response = test_client.post(f'datafile/{datafile_id}/setup_notify',
                                data=json.dumps([
                                  dict(name='cat_var', datatype='numerical'),
                                  dict(name='num_var', datatype='non-numerical')
                                ]), content_type='application/json')
  assert response.json == {}
  assert response.status_code == 201

  response = test_client.get(f'datafile/{datafile_id}/features')
  assert response.status_code == 200
  data = response.json
  assert len(data) == 2
  assert data[0]['name'] == 'cat_var'
  assert data[0]['dtype'] == 'numerical'
  assert data[1]['name'] == 'num_var'
  assert data[1]['dtype'] == 'non-numerical'

def test_api_datafile_notify_setup_error(test_client, datafile_id):

  response = test_client.post(f'datafile/{datafile_id}/setup_notify',
                                data=json.dumps([
                                  dict(name='cat_var', datatype='numerical'),
                                  dict(name='num_var', datatype='non-numerical')
                                ]), content_type='application/json')
  assert response.json == {}
  assert response.status_code == 201

  response = test_client.post(f'datafile/{datafile_id}/setup_notify',
                                data=json.dumps({'error': True}), content_type='application/json')
  assert response.status_code == 201

  response = test_client.get(f'datafile/{datafile_id}/features')
  assert response.status_code == 200
  data = response.json
  assert len(data) == 0

def test_api_datafile_request_consolidate_not_checked(test_client, datafile_id):

  response = test_client.post(f'datafile/{datafile_id}/consolidate_request')
  assert response.status_code == 412

def test_api_datafile_request_consolidate(test_client, datafile_id):

  response = test_client.post(f'datafile/{datafile_id}/setup_notify',
                                data=json.dumps([
                                  dict(name='cat_var', datatype='numerical'),
                                  dict(name='num_var', datatype='non-numerical')
                                ]), content_type='application/json')
  assert response.status_code == 201

  response = test_client.post(f'datafile/{datafile_id}/consolidate_request')
  assert response.status_code == 201

def test_api_datafile_notify_consolidation(test_client, datafile_id):

  response = test_client.post(f'datafile/{datafile_id}/consolidate_notify')
  assert response.status_code == 201

  response = test_client.get(f'datafile/{datafile_id}')
  assert response.status_code == 200
  data = response.json
  assert data['consolidated'] == True
