from data_models.party import Party


def get_parties():
    return Party.select()


def get_parties_per_case(page: int = 1, limit: int = 100):
    return Party.select().paginate(page, limit)


def get_cases_for_party(name: str):
    return Party.select(Party.case_id).where(Party.name == name)


def get_party(id: int):
    return Party.get_by_id(id)
