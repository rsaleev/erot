from typing import List 

from pydantic import BaseModel



"""
Описание моделей ORM в атрибуте model после загрузки и инициализации

dict -> Pydantic

https://tortoise-orm.readthedocs.io/en/latest/models.html#tortoise.models.Model.describe

https://tortoise-orm.readthedocs.io/en/latest/fields.html#tortoise.fields.base.Field.describe
"""
class FieldDescription(BaseModel):
    name:str
    field_type:str
    python_type:str

class ModelDescription(BaseModel):
    name:str
    table:str 
    data_fields:List
    backward_fk_fields:List[FieldDescription]
    backward_o2o_fields:List[FieldDescription]
    fk_fields:List[FieldDescription]
    o2o_fields:List[FieldDescription]
    m2m_fields:List[FieldDescription]