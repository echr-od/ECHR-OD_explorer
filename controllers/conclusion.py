from echr.data_models.conclusion import Conclusion


def get_conclusions():
    return Conclusion.select()


def get_conclusion(id: int):
    return Conclusion.get_by_id(id)
