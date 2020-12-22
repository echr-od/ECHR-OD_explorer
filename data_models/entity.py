import peewee as pw
from data_models.base import BaseModel
from data_models.judgment import JudgmentElement
from data_models.case import Case

class Entity(BaseModel):
    id = pw.AutoField()
    text = pw.CharField()
    label = pw.CharField()


class EntityJudgmentElement(BaseModel):
    entity = pw.ForeignKeyField(Entity, backref='element')
    element = pw.ForeignKeyField(JudgmentElement, backref='entity')
    start = pw.IntegerField()
    end = pw.IntegerField()

    class Meta:
        primary_key = pw.CompositeKey('entity', 'element', 'start', 'end')

class EntityCase(BaseModel):
    id = pw.AutoField()
    entity = pw.ForeignKeyField(Entity, backref='cases')
    case = pw.ForeignKeyField(Case, backref='entities')
