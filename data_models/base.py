import peewee as pw

db = pw.SqliteDatabase('./echr-db.db', pragmas={'foreign_keys': 1})


class BaseModel(pw.Model):
    class Meta:
        database = db
