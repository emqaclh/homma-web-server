from __future__ import annotations

import uuid

from mongoengine import *
from flask_mongoengine import BaseQuerySet

from .datafile import DataFile

class Session(Document):

  unique_id = StringField(max_length=32, required=True, primary_key=True, default= lambda: uuid.uuid4().hex)
  name = StringField(max_length=128, required=True)
  datafiles = ListField(ReferenceField(DataFile, reverse_delete_rule=PULL))

  def set_name(self, name: str) -> Session:
    self.name = name
    self.save()
    self.reload()
    return self
  
  def to_dict(self, deep=False) -> dict:
    dict_repr = dict(
      unique_id = self.unique_id,
      name = self.name,
      datafiles = [datafile.tag if not deep else datafile.to_dict() for datafile in self.datafiles]
    )
    return dict_repr
  
  meta = { 'collection': 'sessions', 'queryset_class': BaseQuerySet}