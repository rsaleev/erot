from pydantic import BaseModel, Extra

class AbstractModel(BaseModel):

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
        extra = Extra.allow