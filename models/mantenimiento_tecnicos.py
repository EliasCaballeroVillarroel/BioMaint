from sqlalchemy import ForeignKey, Table, Column
from database.base import Base

mantenimiento_tecnicos = Table(
    "mantenimiento_tecnicos",
    Base.metadata,
    Column("mantenimiento_id", ForeignKey("mantenimientos.id"), primary_key=True),
    Column("tecnico_id", ForeignKey("tecnicos.id"), primary_key=True),
)
