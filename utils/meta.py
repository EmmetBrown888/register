import ormar

from core.db import metadata, database


class MainMeta(ormar.ModelMeta):
    metadata = metadata
    database = database
