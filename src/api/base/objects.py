from copy import deepcopy, copy
from typing import Any, List, Optional

from pydantic import BaseModel, Extra

from .schema import Database, Document, Mapping, SchemaColumn


class Attribute(BaseModel):
    name: str
    value: Optional[Any]
    document: Document
    database: Optional[Database]
    mapping: Optional[List[Mapping]]

    class Config:
        extra = Extra.allow
   
class Object:

    __slots__=('attributes', 'name')

    def __init__(self, name: str):
        self.attributes: List[Attribute] = []
        self.name = name

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

    def clear(self):
        for attr in self.attributes:
            attr.value = None
