from playhouse.shortcuts import dict_to_model

from datetime import datetime
import json

from data_models.base import db
from data_models.case import Case
from data_models.article import Article
from data_models.conclusion import Conclusion, ConclusionCase, ConclusionDetail, ConclusionMention
from data_models.detail import Detail
from data_models.mention import Mention
from data_models.party import Party, PartyCase
from data_models.kpthesaurus import KPThesaurus
from data_models.representative import Representative, RepresentativeCase
from data_models.issue import Issue
from data_models.documentcollectionid import DocumentCollectionId
from data_models.extractedappno import ExtractedApp
from data_models.scl import SCL, SCLCase
from data_models.decisionbody import DecisionBodyMember, DecisionBodyCase
from data_models.externalsource import ExternalSource

DATABASE_JSON_FILE = 'statics/data/releases/2.0.0/unstructured/cases.json'


def create_tables():
    with db:
        db.create_tables([Case, Article, Conclusion, ConclusionCase, DecisionBodyMember, DecisionBodyCase,
                          ConclusionDetail, Detail, ConclusionMention,
                          Mention, Party, PartyCase, Representative, RepresentativeCase, KPThesaurus, ExternalSource,
                          Issue, DocumentCollectionId, ExtractedApp, SCL, SCLCase])


create_tables()
db.connect()

with open(DATABASE_JSON_FILE) as f:
    cases = json.load(f)

with db.atomic():
    for case in cases:

        print(case['itemid'])
        date_keys = ['decisiondate', 'introductiondate', 'judgementdate', 'kpdate']
        for k in date_keys:
            if case[k]:
                case[k] = datetime.strptime(case[k], '%d/%m/%Y %H:%M:%S')
            else:
                del case[k]
        parties = case.get('parties', [])
        if 'parties' in case:
            del case['parties']
        decisionbody = case.get('decision_body', [])
        if 'decision_body' in case:
            del case['decision_body']
        representedby = case.get('representedby', [])
        if 'representedby' in case:
            del case['representedby']
        kpthesaurus = case.get('kpthesaurus', [])
        if 'kpthesaurus' in case:
            del case['kpthesaurus']
        issues = case.get('issue', [])
        if 'issue' in case:
            del case['issue']
        documentcollectionid = case.get('documentcollectionid', [])
        if 'documentcollectionid' in case:
            del case['documentcollectionid']
        extractedappno = case.get('extractedappno', [])
        if 'extractedappno' in case:
            del case['extractedappno']
        externalsources = case.get('externalsources', [])
        if 'externalsources' in case:
            del case['externalsources']
        scls = case.get('scl', [])
        if 'scl' in case:
            del case['scl']
        case['judgment'] = case['content']['{}.docx'.format(case['itemid'])]
        case['originatingbody_name'] = case['originatingbody']['name']
        case['originatingbody_type'] = case['originatingbody']['type']
        del case['originatingbody']
        i = dict_to_model(Case, case, ignore_unknown=True)
        try:
            i.save(force_insert=True)
        except Exception as e:
            print(e)

        for scl in scls:
            r = SCL.get_or_create(name=scl.title())
            SCLCase.get_or_create(scl=r[0], case=i)

        for source in externalsources:
            ExternalSource.get_or_create(name=source, case=i)

        for appno in extractedappno:
            ExtractedApp.get_or_create(name=appno, case=i)

        for doc in documentcollectionid:
            DocumentCollectionId.get_or_create(name=doc, case=i)

        for issue in issues:
            Issue.get_or_create(name=issue, case=i)

        for kp in kpthesaurus:
            KPThesaurus.get_or_create(name=kp, case=i)

        for representative in representedby:
            r = Representative.get_or_create(name=representative.title())
            RepresentativeCase.get_or_create(representative=r[0], case=i)

        for member in decisionbody:
            bodymember = DecisionBodyMember.get_or_create(name=member['name'], role=member.get('role', '').title())
            DecisionBodyCase.get_or_create(member=bodymember[0], case=i)

        for party in parties:
            p = Party.get_or_create(name=party)
            PartyCase.get_or_create(party=p[0], case=i)

        for article in case['article']:
            Article.get_or_create(title=article, case=i)
        for element in case['conclusion']:
            details = element.get('details', [])
            if 'details' in element:
                del element['details']
            mentions = element.get('mentions', [])
            if 'mentions' in element:
                del element['mentions']
            c = Conclusion.get_or_create(**element)
            ConclusionCase.get_or_create(conclusion=c[0], case=i)
            for detail in details:
                d = Detail.get_or_create(detail=detail)
                ConclusionDetail.get_or_create(detail=d[0], conclusion=c[0])
            for mention in mentions:
                m = Mention.get_or_create(mention=mention)
                ConclusionMention.get_or_create(mention=m[0], conclusion=c[0])

    # Adjust ExtractedAppNo
    query = list(ExtractedApp.select())
    for i, e in enumerate(query):
        print('{}/{} - {}'.format(i, len(query), e.name))
        r = list(Case.select().where(Case.appno == e.name))
        if r:
            e.update(isechr=True)
            e.save()

case = Case.select().limit(1)[0]
print(case)
print(list(case.parties))
print(list(case.conclusions))
db.close()
