from echr.data_models.scl import SCL


def get_scls():
    return SCL.select()


def get_scl(id: int):
    return SCL.get_by_id(id)
