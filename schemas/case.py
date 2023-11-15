from datetime import datetime
from pydantic import BaseModel
from typing import List


class Case(BaseModel):
    itemid: str
    docname: str
    doctypebranch: str
    documentcollectionid: List[str]
    ecli: str
    externalsources: str
    extractedappno: List[str]
    importance: int
    issue: str
    applicability: str
    appno: str

    decisiondate: datetime = None
    introductiondate: datetime = None
    judgementdate: datetime = None
    kpdate: datetime = None
    kpthesaurus: List[str]
    languageisocode: str
    originatingbody: str
    parties: List[str]
    rank: str
    representedby: List[str]
    respondent: str
    scl: List[str]
    separateopinion: str
    typedescription: str

    class Config:
        orm_mode = True
