import peewee as pw
from data_models.base import BaseModel
from data_models.case import Case
from data_models.detail import Detail
from data_models.mention import Mention


class Conclusion(BaseModel):
    id = pw.AutoField()
    article = pw.CharField(null=True)
    element = pw.CharField()
    base_article = pw.CharField(null=True)
    type = pw.CharField()


class ConclusionDetail(BaseModel):
    detail = pw.ForeignKeyField(Detail, backref='in_ccl')
    conclusion = pw.ForeignKeyField(Conclusion, backref='details')


class ConclusionMention(BaseModel):
    mention = pw.ForeignKeyField(Mention, backref='in_ccl')
    conclusion = pw.ForeignKeyField(Conclusion, backref='mentions')


class ConclusionCase(BaseModel):
    conclusion = pw.ForeignKeyField(Conclusion, backref='in_cases')
    case = pw.ForeignKeyField(Case, backref='conclusions')

    class Meta:
        primary_key = pw.CompositeKey('conclusion', 'case')
