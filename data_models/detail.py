import peewee as pw
from data_models.base import BaseModel


class Detail(BaseModel):
    id = pw.AutoField()
    detail = pw.CharField()
