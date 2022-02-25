from typing import Any 


from tortoise.models import Model
from tortoise.fields import IntField, CharField, CharField, ForeignKeyField, ReverseRelation
from tortoise.models import Model
from tortoise.fields import IntField, ForeignKeyField, CharField, ReverseRelation, TextField, UUIDField, DatetimeField
from src.database.custom_fields import TextArrayField
from tortoise.manager import Manager




class ParentModel(Model):

    id = IntField(pk=True)


    class Meta:
        asbstract = True

    class PydanticMeta:
        exclude = ["id"]


class Base(ParentModel):
    req_id = CharField(max_length=20, unqiue=True, index=True, null=False)
    # req_content = TextField(null=False)
    # req_link = TextField(null=True)
    req_guid = UUIDField(null=False, index=True, unique=True)

    created = DatetimeField(auto_now_add=True, index=True)
    updated = DatetimeField(auto_now=True, index=True)
    
    #sanctions: ReverseRelation['Sanction']
    #physical_sanctions: ReverseRelation['PhysicalSanction']

    def __str__(self):
        return self.req_guid


    class Meta:
        app = 'erot'
        table_description = "Основные данные ОТ"


class AbstractSanction(Model):

    id = IntField(pk=True)
    snct_subject = IntField(null=False)
    # snct_title = TextArrayField(null=True)
    # snct_content = TextArrayField(null=True)
    # snct_comments = TextArrayField(null=True)

    class Meta:
        abstract = True

class Sanction(AbstractSanction):
    
    base = ForeignKeyField('erot.Base',
                               to_field='req_guid', db_constraint=False)

    class Meta:
        app = "erot"
        table = 'sanction'
        table_description = "Санкциии за несоблюдение ОТ"

class PhysicalSanction(Sanction):

    
    base = ForeignKeyField('erot.Base',
                               to_field='req_guid', db_constraint=False)


    class Meta:
        app = "erot"
        table = 'sanction'
        table_description = "Санкциии за несоблюдение ОТ"

class ExecutiveSanction(Sanction):


    # def __init__(**kwargs):
    #     return super().__init__(**kwargs)

    base = ForeignKeyField('erot.Base',
                               to_field='req_guid', db_constraint=False)
    
    class Meta:
        app = "erot"
        table = 'sanction'
        table_description = "Санкциии за несоблюдение ОТ"


__models__ = [Base, Sanction]