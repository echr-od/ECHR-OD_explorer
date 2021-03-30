import peewee as pw
from echr.data_models.base import BaseModel
from echr.data_models.case import Case

class JudgmentElement(BaseModel):
    id = pw.AutoField()
    case = pw.ForeignKeyField(Case, backref='judgement_elements')
    content = pw.CharField()
    parent_element = pw.IntegerField(null=True)
    is_paragraph = pw.BooleanField()
    section_name = pw.CharField(null=True)


class JudgmentClosure(BaseModel):
    parent = pw.ForeignKeyField(JudgmentElement, backref='parent', null=True)
    child = pw.ForeignKeyField(JudgmentElement, backref='child')
    depth = pw.IntegerField()

    class Meta:
        primary_key = pw.CompositeKey('parent', 'child', 'depth')
