from copy import deepcopy
from importlib import import_module
from typing import Any, List, Optional
import asyncio
from attr import attr
from pydantic import BaseModel

from src.database.models.erot import ErotModel
from .schema import Mapping, SchemaColumn, Document, Database
from .transformer import BaseTransformer


class Attribute(BaseModel):
    name: str
    value: Optional[Any]
    document: Document
    database: Database
    mapping: Optional[List[Mapping]]
   
class Object:

    def __init__(self, name: str):
        self.attributes: List[Attribute] = []
        self.name = name

    def copy(self):
        return deepcopy(self)

    def add_field(self, schema_column: SchemaColumn):
        """
        Создание объекта через встроенную функцию type и добавление в массив атрибутов

        Args:
            attr_schema (schema.DocumentSchemaColumn): структура объекта 
        """
        attribute = Attribute(**schema_column.dict())
        self.attributes.append(attribute)

    def del_field(self):
        raise NotImplementedError

    def upd_field(self, schema_column):
        raise NotImplementedError