import peewee as pw

db = pw.SqliteDatabase(None, pragmas={'foreign_keys': 1})


class BaseModel(pw.Model):
    class Meta:
        database = db
