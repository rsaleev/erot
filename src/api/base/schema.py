from typing import List, Optional, List, Union, Any, Type, Dict

from src.api.base.model import AbstractModel

from src.api.base.transformer import BaseTransformer

from src.database.models.erot import ErotModel

from pydantic import Field


class Format(AbstractModel):
    formatter: str
    options: List[str]
    output:Optional[Dict[str, str]]
    attribute:str




class Document(AbstractModel):
    regex: str
    index: int
    optional: bool
    format: Union[None, List[Format]]


class Mapping(AbstractModel):
    input: str
    link: str
    output: str

    
class Database(AbstractModel):
    orm: str
    attribute: str
    param: Dict[str, str]
    format:Optional[List[Format]]

class SchemaColumn(AbstractModel):
    name: str
    document: Document
    mapping: Optional[List[Mapping]]
    database: Optional[Database]

    
class DocumentSchemaMissingColumns(AbstractModel):

    required: Optional[List[str]]
    optional: Optional[List[str]]

class HeaderAttribute(AbstractModel):
    name: str
    optional: bool
class DocumentSchemaData(AbstractModel):

    name: str = Field(..., alias='schema')
    header: Optional[List[HeaderAttribute]]
    columns: List[SchemaColumn]
    missing: Optional[DocumentSchemaMissingColumns]

class DocumentSchemaResponse(AbstractModel):

    data: Optional[DocumentSchemaData]
    error: Optional[str]
