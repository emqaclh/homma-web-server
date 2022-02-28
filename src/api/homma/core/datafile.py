from __future__ import annotations
from pyexpat import features

import uuid

from typing import TypedDict
from numpy import dtype
from mongoengine import *
from flask_mongoengine import BaseQuerySet

from .feature import Feature

class SetupType(TypedDict):
  sep: str
  decimal: str
  encoding: str

class DataFile(Document):

  unique_id = StringField(max_length=32, required=True, primary_key=True, default= lambda: uuid.uuid4().hex)
  path = StringField(max_length=64, required=True)
  tag = StringField(max_length=32, required=True)
  setup = DictField(default = lambda: dict(encoding='utf-8', sep=';', decimal=','))
  setup_attempt_key = StringField(max_length=32, default= lambda: uuid.uuid4().hex)
  consolidated = BooleanField(default=False)
  features = ListField(ReferenceField(Feature, reverse_delete_rule=PULL), default=lambda: [])
  
  def set_tag(self, tag: str) -> DataFile:
    self.tag = tag
    self.save()
    self.reload()
    return self

  def set_setup(self, setup: dict) -> DataFile:
    self.setup = setup
    self.save()
    self.reload()
    return self

  def reset_setup_key(self) -> None:
    self.setup_attempt_key = uuid.uuid4().hex
    self.save()
    self.reload()

  def set_features(self, features: list) -> None:
    for feature in features:
      new_feature = Feature(name=feature['name'], dtype=feature['datatype'])
      new_feature.save()
      self.features.append(new_feature)
    self.save()
    self.reload()

  def clear_features(self) -> None:
    for feature in self.features:
      feature.delete()
    self.features = []
    self.save()
    self.reload()

  def to_dict(self, deep=False) -> dict:
    dict_repr = dict(
      unique_id = self.unique_id,
      path = self.path,
      tag = self.tag,
      consolidated = self.consolidated,
      setup=self.setup,
      features = [feature.name if not deep else feature.to_dict() for feature in self.features]
    )
    return dict_repr
  
  meta = { 'collection': 'datafiles', 'queryset_class': BaseQuerySet }