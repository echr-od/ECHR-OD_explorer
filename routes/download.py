import csv
import json

from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse

from config.template import templates
from controllers import case as c_case
from echr.data_models.case import Case
from utils.config import config

router = APIRouter()


@router.route('/download/', include_in_schema=False)
async def download(request):
    template = "download.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)


@router.get("/download/{version}/{format}/{type_}/{extension}", include_in_schema=False)
async def download_files(version: str, format: str, type_: str, extension: str):
    schema = {
        'all': {
            'all': {
                'zip': lambda a, b, c, d: download_all_zip(a, b, c, d),
                'sqlite': lambda a, b, c, d: download_all_sqlite(a, b, c, d)
            }
        },
        'structured': {
            'cases': {
                'csv': lambda a, b, c, d: download_file(a, b, c, d),
                'json': lambda a, b, c, d: download_file(a, b, c, d)
            },
            'matrice_decision_body': {
                'json': lambda a, b, c, d: download_file(a, b, c, d)
            },
            'matrice_appnos': {
                'json': lambda a, b, c, d: download_file(a, b, c, d)
            },
            'matrice_scl': {
                'json': lambda a, b, c, d: download_file(a, b, c, d)
            },
            'matrice_representatives': {
                'json': lambda a, b, c, d: download_file(a, b, c, d)
            },
            'bow': {
                'libsvm': lambda a, b, c, d: download_file(a, b, c, 'zip')
            },
            'tfidf': {
                'libsvm': lambda a, b, c, d: download_file(a, b, c, 'zip')
            }
        },
        'unstructured': {
            'cases': {
                'json': lambda a, b, c, d: download_file(a, b, c, d)
            }
        },
        'raw': {
            'judgments': {
                'docx': lambda a, b, c, d: download_file(a, b, c, 'zip')
            },
            'normalized': {
                'txt': lambda a, b, c, d: download_file(a, b, c, 'zip')
            }
        }
    }
    if format not in schema:
        raise HTTPException(status_code=404, detail="Invalid dataset flavor {}".format(format))
    else:
        types = schema[format]
        if type_ in types:
            extensions = types[type_]
            if extension in extensions:
                return extensions[extension](version, format, type_, extension)
            else:
                raise HTTPException(status_code=404,
                                    detail="Invalid extension {} for format {} and type {}".format(extension, format,
                                                                                                   type_))
        else:
            raise HTTPException(status_code=404, detail="Invalid type {} for format {}".format(extension, format))


def download_all_sqlite(version, format, type_, extension):
    v = version.replace('.', '_')
    sqlite_path = '{}/{}/structured/echr-db.db'.format(config()['data']['data_folder'], config()['data']['build_name'], format, v)
    return FileResponse(sqlite_path, filename='echr_{}.db'.format(v))


def download_all_zip(version, format, type_, extension):
    v = version.replace('.', '_')
    archive_path = '{}/{}/all.zip'.format(config()['data']['data_folder'], config()['data']['build_name'], v)
    return FileResponse(archive_path, filename='echr_{}.zip'.format(v))


def download_file(version, format, type_, extension):
    v = version.replace('.', '_')
    archive_path = '{}/{}/{}/{}.{}'.format(config()['data']['data_folder'], config()['data']['build_name'], format, type_, extension)
    return FileResponse(archive_path, filename='echr_{}_{}_{}.{}'.format(v, format, type_, extension))


def format_structured_json():
    cases_id = Case.select(Case.itemid)
    cases = []
    representents = []
    for case_id in cases_id:
        c = c_case.get_case_info(case_id)
        parties = c['parties']
        c['party_1'] = parties[0]
        c['party_2'] = parties[1]
        c.update(flatten_simply_dict(c, 'originatingbody'))
        c['respondent'] = c['respondent'].split(';')[0]
        c['applicability'] = c['applicability'].split(';')[0]
        del c['originatingbody']
        del c['parties']
        del c['appno']
        del c['judgment']
        for d in c['documents']:
            c['documents'][d] = c['documents'][d]['uri'] if c['documents'][d]['available'] else None
        c.update(flatten_simply_dict(c, 'documents'))
        del c['documents']
        c['country'] = c['country']['name']
        del c['articles']
        representents.append(c['representedby'])
        del c['representedby']
        del c['extractedapps']
        del c['conclusions']
        del c['decisionbody']
        del c['scl']
        cases.append(c)
    return cases


def flatten_simply_dict(data, key):
    flat = {}
    for k in data.get(key, []):
        flat['{}_{}'.format(key, k)] = data[key][k]
    return flat


def download_structured_csv(version):
    json_cases = format_structured_json()
    write_flat_json_to_csv(json_cases, 'test.csv')
    return FileResponse('test.csv', filename='test.csv')


def write_json(json_data, path):
    with open(path, "w") as outfile:
        json.dump(json_data, outfile, indent=4)


def write_flat_json_to_csv(json_data, path):
    csv_file = open(path, 'w')
    csv_writer = csv.writer(csv_file)
    count = 0
    for r in json_data:
        if count == 0:
            header = r.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(r.values())
    csv_file.close()
    return json_data
