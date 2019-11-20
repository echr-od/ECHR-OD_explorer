import peewee as pw
from data_models.base import BaseModel
from data_models.case import Case


class Issue(BaseModel):
    name = pw.CharField()
    case = pw.ForeignKeyField(Case, backref='issues')
