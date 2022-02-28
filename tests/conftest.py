import pytest

import pandas as pd
import numpy as np

from src.main import create_app

@pytest.fixture(scope='session')
def test_client():

  flask_app = create_app(db_config = {'db': 'mongoenginetest', 'host': 'mongomock://localhost'}, testing=True)

  with flask_app.test_client() as testing_client:
    with flask_app.app_context():
      yield testing_client

def generate_temp_dataset():
    data = pd.DataFrame()
    data['num_var_1'] = np.random.rand(15_000)
    data['cat_var_1'] = np.random.randint(192, 199, 15_000)
    return data

@pytest.fixture(scope='session')
def temp_csv(tmp_path_factory):
    data = generate_temp_dataset()
    path = tmp_path_factory.mktemp('temp') / 'test.csv'
    data.to_csv(path)
    return str(path)