import peewee as pw
from data_models.base import BaseModel


class Mention(BaseModel):
    id = pw.AutoField()
    mention = pw.CharField()
