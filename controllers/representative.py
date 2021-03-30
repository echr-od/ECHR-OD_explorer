from echr.data_models.representative import Representative


def get_representatives():
    return Representative.select()


def get_representative(id: int):
    return Representative.get_by_id(id)
