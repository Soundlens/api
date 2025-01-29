# # from app.api.services.tags import TagService
from functools import wraps
from typing import List

from app import db


class NewFileData:
    def __init__(self, file_name, stream):
        self.file_name = file_name
        self.stream = stream


class NewTagData:
    def __init__(self, obj):
        self.name = obj["name"]
        self.type = obj["type"]
        self.color = obj["color"]


class SampleElementData:
    def __init__(self, batch_id, plant_id):
        self.batch_id = batch_id
        self.plant_id = plant_id

    def data(self):
        return {"batch_id": self.batch_id, "plant_id": self.plant_id}
