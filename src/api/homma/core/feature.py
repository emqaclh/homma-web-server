import uuid

from mongoengine import *
from flask_mongoengine import BaseQuerySet


class Feature(Document):

    unique_id = StringField(
        max_length=32, required=True, primary_key=True, default=lambda: uuid.uuid4().hex
    )
    name = StringField(max_length=128, required=True)
    dtype = StringField(required=True, choices=("numerical", "non-numerical"))
    description = DictField()

    def to_dict(self, include_description=False) -> dict:
        dict_repr = dict(unique_id=self.unique_id, name=self.name, dtype=self.dtype)
        if include_description:
            dict_repr["description"] = self.description
        return dict_repr

    meta = {"collection": "features", "queryset_class": BaseQuerySet}
