from typing import TypeVar

from collections import ChainMap

from tortoise.fields import (CharField, DatetimeField, DateField, TextField,
                             UUIDField, ReverseRelation, IntField,
                             OneToOneField, ForeignKeyField, JSONField)
from tortoise.models import Model
from tortoise.functions import Max

from src.database.custom_fields import TextArrayField

MODEL = TypeVar("MODEL", bound="Model")


class ParentModel(Model):

    id = IntField(pk=True)
    req_guid = UUIDField(null=False, index=True, unique=True)

    def get_fk(self):
        return {'req_guid_id': self.req_guid}

    class Meta:
        asbstract = True

    class PydanticMeta:
        exclude = ["id"]


class ChildModel(Model):

    id = IntField(pk=True)

    def to_dict(self):
        output = {}
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                output.update({k: v})
        return output

    class Meta:
        asbstract = True

    class PydanticMeta:
        exclude = ["id"]


class Base(ParentModel):
    req_id = CharField(max_length=20, unqiue=True, index=True, null=False)
    req_content = TextField(null=False)
    created = DatetimeField(auto_now_add=True, index=True)
    updated = DatetimeField(auto_now=True, index=True)
    req_link = TextField(null=True)
    req_guid = UUIDField(null=False, index=True, unique=True)

    descriptions: ReverseRelation['Description']
    controls: ReverseRelation['Control']
    compliances: ReverseRelation['Compliance']
    liabilities: ReverseRelation['Liability']
    sanctions: ReverseRelation['Sanction']

    class Meta:
        app = 'erot'
        table = 'req_base'
        table_description = "Основные данные ОТ"


class Description(ChildModel):
    desc_publication_status = IntField(null=True)
    desc_publication_date = DateField(null=True)
    desc_work_status = IntField(null=True)
    desc_regulation_level = IntField(null=True)
    desc_act_requisites = CharField(max_length=255)
    desc_act_text = TextField()
    desc_valid_to = DateField(null=True)
    desc_validity_status = IntField(null=True)

    req_guid = OneToOneField('erot.Base',
                             to_field='req_guid',
                             related_name='descriptions')

    class Meta:
        app = 'erot'
        table = 'req_description'
        table_description = "Описание ОТ"


class Control(ChildModel):
    ctrl_objects = TextArrayField(null=True)
    ctrl_subjects_categories = TextArrayField(null=True)
    ctrl_subjects_categories_ext = TextArrayField(null=True)
    ctrl_evaluation_form = TextField(null=True)
    ctrl_control_type = IntField(null=True)
    ctrl_data_alter_org = IntField(null=True)
    ctrl_verifying_org = IntField(null=True)
    ctrl_verifying_question = TextField(null=True)

    req_guid = OneToOneField('erot.Base',
                             to_field='req_guid',
                             related_name='controls')

    class Meta:
        app = 'erot'
        table = 'req_control'
        table_description = "Контрольно-надзорная деятельность"


class Compliance(ChildModel):
    cmpl_act_type = TextField(null=False)
    cmpl_act_title = TextField(null=False)
    cmpl_act_text = TextField(null=True)
    cmpl_act_approved_org = TextField(null=False)
    cmpl_act_approved_date = DateField(null=True)
    cmpl_act_number = CharField(max_length=20)
    cmpl_act_id = CharField(max_length=10, null=False)
    cmpl_act_link = TextField(null=True)

    req_guid = OneToOneField('erot.Base',
                             to_field='req_guid',
                             related_name='acts')

    class Meta:
        app = 'erot'
        table = 'req_compliance'
        table_description = "Соответствие ОТ"


class Liability(ChildModel):
    lblt_act_title = TextField(null=False)
    lblt_act_article = TextField(null=True)
    lblt_act_clause = TextField(null=True)
    lblt_act_text = TextField(null=True)
    lblt_organization = TextField(null=False)
    lblt_subjects = TextArrayField(null=False)

    req_guid = OneToOneField('erot.Base',
                             to_field='req_guid',
                             related_name='liabilities')

    class Meta:
        app = "erot"
        table = "req_liability"
        table_description = "Ответственность за несоблюдение ОТ"


class Sanction(ChildModel):
    id = IntField(pk=True)
    snct_subject = TextField(null=False)
    snct_title = TextField(null=True)
    snct_content = TextField(null=True)
    snct_comments = TextField(null=True)

    req_guid = ForeignKeyField('erot.Base',
                               to_field='req_guid',
                               related_name='sanctions')

    class Meta:
        app = "erot"
        table = 'req_sanctions'
        table_description = "Санкциии за несоблюдение ОТ"


class AbstractSanction(ChildModel):
    """
    Абстрактная модель без инициалазиции в БД.
    
    Включает в себя метод для сохранения данных в БД через модель Sanction
    """
    id = IntField(pk=True)
    snct_subject = TextField(null=False)
    snct_title = TextField(null=True)
    snct_content = TextField(null=True)
    snct_comments = TextField(null=True)
    req_guid_id = UUIDField()



    @staticmethod
    async def _get_last_pk():
        record_ids = await Sanction.all()
        try:
            next_record_id = max(s.id for s in record_ids) + 1
        except:
            next_record_id = 1
        finally:
            return next_record_id


    @staticmethod
    async def create(**kwargs):
        """
        перегрузка метода create(**kwargs) для типа tortose.models.Model

        1. Инициализируется экземляра класса с передачей атрибутов
        2. Создается обращение к методу create(**kwargs) класса Sanction для реализации записи в БД

        """
        instance = AbstractSanction()
        instance._set_kwargs(kwargs)
        data = dict(
            ChainMap(*[{
                f[0]: f[1]
            } for f in list(instance.__iter__())]))
        
        data.update({'id': AbstractSanction._get_last_pk})
        record = await Sanction.create(**data)
        return record

    @staticmethod
    async def get_or_none(*args, **kwargs):
        record = await Sanction.get_or_none(**kwargs)
        return record

    async def update_or_create(self):
        data = {}
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                data.update({k:v})
        data.update({'id': AbstractSanction._get_last_pk})
        await Sanction.update_or_create(**data)

    class Meta:
        abstract = True


class PhysicalSanction(AbstractSanction):
    """
    PhysicalSanction 

    модель для соотношения извлекаемых данных с таблицей

    соотносится с данным о санкции в отношении физических лиц
    """
    pass


class SelfemployedSanction(AbstractSanction):
    """
    SelfemployedSanction

    модель для соотношения извлекаемых данных с таблицей

    соотносится с данным о санкции в отношении индивидуальных предпринимателей


    """
    pass


class ExecutiveSanction(AbstractSanction):
    """
    ExecutiveSanction 

    модель для соотношения извлекаемых данных с таблицей

    соотносится с данным о санкции в отношении должностных лиц

    """
    pass


class JuristicSanction(AbstractSanction):
    """
    JuristicSanction 

    модель для соотношения извлекаемых данных с таблицей

    соотносится с данным о санкции в отношении юридических лиц

    """
    pass


class Attribute(ChildModel):
    attr_public_relations = TextArrayField(null=True)
    attr_economic_activities = TextArrayField()
    attr_cost_estimate = TextArrayField(null=True)
    attr_documents_list = TextArrayField(null=True)
    attr_org_data_provision = TextField(null=True)
    attr_org_data_provision_ext = TextField(null=True)
    attr_checklists_links = TextArrayField()
    attr_manuals_links = TextArrayField(null=True)
    attr_reports_links = TextArrayField(null=True)

    req_guid = OneToOneField('erot.Base',
                             to_field='req_guid',
                             related_name='attributes')

    class Meta:
        app = "erot"
        table = 'req_attribute'


class Updates(Model):
    id = IntField(pk=True)
    updated = DatetimeField(auto_now_add=True)
    old = TextField()
    new = TextField()
    column = TextField()
    req_uid = UUIDField(unique=False)

    class Meta:
        app = "erot"
        table = 'updates'


__models__ = [
    Base, Description, Compliance, Liability, Sanction, Control, Attribute,
    Updates
]
