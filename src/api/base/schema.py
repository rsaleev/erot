
from email.header import Header
from typing import List, Optional, List, Union, Any, Type

from pydantic import BaseModel, Field
from pydantic import root_validator, validator

from tortoise.models import Model as ORMModel

from .transformer import BaseTransformer
from .orm import ModelDescription as ORMDescription

class Format(BaseModel):
    formatter:str
    options:List[str]
    _instance:Type[BaseTransformer]


    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True


class Document(BaseModel):
    regex:str
    index:int
    optional:bool
    format:Union[None, List[Format]]



    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True


class Mapping(BaseModel):
    input:str 
    link:str
    output:str 

    class Config:
        arbitrary_types_allowed = True

class Database(BaseModel):
    orm:str
    attribute:str
    _model:ORMModel
    _description:ORMDescription
    additional_param:Optional[str]
    additional_attribute:Optional[str]   

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True 

class SchemaColumn(BaseModel):
    name:str 
    document: Document
    mapping:Optional[List[Mapping]]
    database:Optional[Database]

    class Config:
        arbitrary_types_allowed = True

class DocumentSchemaMissingColumns(BaseModel):

    required:Optional[List[str]]
    optional:Optional[List[str]]

class DocumentSchemaData(BaseModel):

    name:str = Field(..., alias='schema')
    header:Optional[Header]
    columns:List[SchemaColumn]
    missing:Optional[DocumentSchemaMissingColumns]

    class Config:
        arbitrary_types_allowed = True

class DocumentSchemaResponse(BaseModel):

    data:Optional[DocumentSchemaData]
    error:Optional[str]

    class Config:
        arbitrary_types_allowed = True

