from tortoise.fields import (CharField, DatetimeField, DateField, TextField,
                             UUIDField, ReverseRelation, IntField,
                             OneToOneField, ForeignKeyField)
from tortoise.models import Model

from src.database.custom_fields import NumericArrayField, TextArrayField

from src.database.helpers import kwargs_to_pg_types


class ErotModel(Model):

    @classmethod
    async def get(cls, **kwargs):
        return await super().get(**kwargs_to_pg_types(**kwargs))

    @classmethod
    async def get_or_none(cls, **kwargs):
        return await super().get_or_none(**kwargs_to_pg_types(**kwargs))

    class Meta:
        abstract = True


class Base(Model):
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
        table_description = "Основные данные ОТ"


class Description(ErotModel):
    desc_publication_status = IntField(null=True)
    desc_publication_date = DateField(null=True)
    desc_work_status = IntField(null=True)
    desc_regulation_level = IntField(null=True)
    desc_act_requisites = TextArrayField(max_length=255)
    desc_act_text = TextField(null=False)
    desc_valid_to = DateField(null=True)
    desc_validity_status = IntField(null=True)

    req_guid = OneToOneField('erot.Base',
                             to_field='req_guid',
                             related_name='descriptions')

    class Meta:
        app = 'erot'
        table_description = "Описание ОТ"


class Control(ErotModel):
    ctrl_objects = TextField(null=False)
    ctrl_subjects_categories = TextField(null=True)
    ctrl_subjects_categories_ext = TextField(null=True)
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
        table_description = "Контрольно-надзорная деятельность"


class Compliance(ErotModel):
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
        table_description = "Соответствие ОТ"


class Liability(Model):
    lblt_act_title = TextField(null=False)
    lblt_act_article = TextField(null=False)
    lblt_act_clause = TextField(null=False)
    lblt_act_text = TextField(null=True)
    lblt_organization = NumericArrayField(null=True)
    lblt_subjects = NumericArrayField(null=False)

    req_guid = OneToOneField('erot.Base',
                             to_field='req_guid',
                             related_name='liabilities')

    class Meta:
        app = "erot"
        table_description = "Ответственность за несоблюдение ОТ"


class Sanction(Model):
    id = IntField(pk=True)
    snct_subject = IntField(null=False)
    snct_title = TextField(null=True)
    snct_content = TextField(null=True)
    snct_comments = TextField(null=True)

    req_guid = ForeignKeyField('erot.Base',
                               to_field='req_guid',
                               related_name='sanctions')

    @classmethod
    async def create(cls, **kwargs):
        """
        Sanction.create(cls, **kwargs)

        перезагрузка метода для создания одиночных записей, если в значениях указаны несколько субъектов
        """
        if isinstance(kwargs['snct_title'], list):
            single_data = {}
            for title in kwargs['snct_title']:
                single_data['snct_subject'] = kwargs['snct_subject']
                single_data['snct_title'] = title
                single_data['snct_content'] = next(
                    (c.replace(title, '').replace(':', '').strip()
                     for c in kwargs['snct_content'] if c.rfind(title) > -1),
                    None)
                single_data['snct_comments'] =next(
                    (c.replace(title, '').replace(':', '').strip()
                     for c in kwargs['snct_comments'] if c.rfind(title) > -1),
                    None)
                single_data.update(kwargs['req_guid_id'])
                await super().create(**single_data)
        else:
            await super().create(**kwargs)


    @classmethod
    async def get(cls, **kwargs):
        if isinstance(['snct_title'], list):
            output = []
            single_data = {}
            for title in kwargs['snct_title']:
                single_data['snct_subject'] = kwargs['snct_subject']
                single_data['snct_title'] = title
                single_data['snct_content'] = next(
                    (c.replace(title, '').replace(':', '').strip()
                     for c in kwargs['snct_content'] if c.rfind(title) > -1),
                    None)
                single_data['snct_comments'] =next(
                    (c.replace(title, '').replace(':', '').strip()
                     for c in kwargs['snct_comments'] if c.rfind(title) > -1),
                    None)
                single_data.update(kwargs['req_guid'])
                output.append(await super().get(**single_data))
        else:
            return await super().get(**kwargs)
        

    @classmethod
    async def get_or_none(cls, **kwargs):
        if isinstance(kwargs['snct_title'], list):
            output = []
            single_data = {}
            for title in kwargs['snct_title']:
                single_data['snct_subject'] = kwargs['snct_subject']
                single_data['snct_title'] = title
                single_data['snct_content'] = next(
                    (c.replace(title, '').replace(':', '').strip()
                     for c in kwargs['snct_content'] if c.rfind(title) > -1),
                    None)
                if kwargs['snct_comments']:
                    single_data['snct_comments'] =next(
                        (c.replace(title, '').replace(':', '').strip()
                        for c in kwargs['snct_comments'] if c.rfind(title) > -1),
                        None)
                single_data.update({'req_guid_id':kwargs['req_guid_id']})
                output.append(await super().get_or_none(**single_data))
            return output
        else:
            return await super().get_or_none(**kwargs)
                

    class Meta:
        app = "erot"
        table_description = "Санкциии за несоблюдение ОТ"


class Attribute(ErotModel):
    attr_public_relations = TextArrayField(null=True)
    attr_economic_activities = TextArrayField()
    attr_cost_estimate = TextArrayField(null=True)
    attr_documents_list = TextArrayField(null=True)
    attr_org_data_provision = TextField(null=True)
    attr_org_data_provision_ext = TextField(null=True)
    attr_checklists_links = TextArrayField(null=True)
    attr_manuals_links = TextArrayField(null=True)
    attr_reports_links = TextArrayField(null=True)

    req_guid = OneToOneField('erot.Base',
                             to_field='req_guid',
                             related_name='attributes')

    class Meta:
        app = "erot"


class Updates(Model):
    id = IntField(pk=True)
    updated = DatetimeField(auto_now_add=True)
    old = TextField()
    new = TextField()
    column = TextField()
    req_uid = UUIDField(unique=False)

    class Meta:
        app = "erot"


__models__ = [
    Base, Description, Compliance, Liability, Sanction, Control, Attribute,
    Updates
]
