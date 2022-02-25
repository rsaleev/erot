from enum import unique
from hashlib import new
from typing import Union, List, Any, Tuple


from tortoise.fields import (CharField, DatetimeField, DateField, TextField,
                             UUIDField, ReverseRelation, IntField,
                             OneToOneField, ForeignKeyField)
                             
from tortoise.models import Model

from src.database.custom_fields import NumericArrayField, TextArrayField

from src.database.helpers import compare_records, model_to_dict

import asyncio

import re

class ErotModel(Model):

    @classmethod
    async def create_or_update(cls, **kwargs):
        """
        create_or_update

        Измененнный метод для обработки массива значений (k:v) на входе или единичного значения (k:v)

        1. Поиск значений в БД

        2.1 Если запись не существует -> создание новой записи

        2.2 Если запись существует:
            2.2.1 Сверка значений в БД и новых значений 
            2.2.2 Обновление записи в БД
            2.2.3 Создание записей в таблице Updates
            2.2.4 Поиск и обновление записи Base
        """
        excluded_keys = ('id', 'parent', 'req_guid_id', 'req_guid')
        tasks = []
        record = await super().get_or_none(req_guid_id=kwargs['parent'].req_guid)
        if not record:
            tasks.append(super().create(**kwargs, req_guid_id=kwargs['parent'].req_guid))
        else:
            record_values = model_to_dict(record)
            if diffs := compare_records(record_values, kwargs, exclude=excluded_keys):
                tasks.append(
                    Updates.bulk_create([
                        Updates(**diff, req_guid=kwargs['parent'].req_guid)
                        for diff in diffs
                    ]))
                record.update_from_dict(kwargs)
                tasks.append(record.save())
                tasks.append(kwargs['parent'].save())
        await asyncio.gather(*tasks)

    class Meta:
        abstract = True


class Base(ErotModel):
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
    cmpl_act_type = IntField(null=True)
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


class Liability(ErotModel):
    lblt_act_title = TextField(null=True)
    lblt_act_article = TextField(null=True)
    lblt_act_clause = TextField(null=True)
    lblt_act_text = TextField(null=True)
    lblt_organization = NumericArrayField(null=True)
    lblt_subjects = NumericArrayField(null=True)

    req_guid = OneToOneField('erot.Base',
                             to_field='req_guid',
                             related_name='liabilities')

    class Meta:
        app = "erot"
        table_description = "Ответственность за несоблюдение ОТ"


class Sanction(ErotModel):
    id = IntField(pk=True)
    snct_subject = IntField(null=False)
    snct_title = TextArrayField(null=True)
    snct_content = TextArrayField(null=True)
    snct_comments = TextArrayField(null=True)

    req_guid = ForeignKeyField('erot.Base',
                               to_field='req_guid',
                               related_name='sanctions')

    @classmethod
    async def create_or_update(cls, **kwargs):
        """
        create_or_update

        Измененнный метод для обработки массива значений (k:v) на входе или единичного значения (k:v)

        1. Поиск значений в БД

        2.1 Если запись не существует -> создание новой записи

        2.2 Если запись существует:
            2.2.1 Сверка значений в БД и новых значений 
            2.2.2 Обновление записи в БД
            2.2.3 Создание записей в таблице Updates
            2.2.4 Поиск и обновление записи Base
        """
        excluded_keys = ('id', 'parent', 'req_guid_id', 'req_guid')
        tasks = []
        record = await super().get_or_none(req_guid_id=kwargs['parent'].req_guid, snct_subject=kwargs['snct_subject'])
        if not record:
            tasks.append(super().create(**kwargs, req_guid_id=kwargs['parent'].req_guid))
        else:
            record_values = model_to_dict(record)
            if diffs := compare_records(record_values, kwargs, exclude=excluded_keys):
                tasks.append(
                    Updates.bulk_create([
                        Updates(**diff, req_guid=kwargs['parent'].req_guid)
                        for diff in diffs
                    ]))
                record.update_from_dict(kwargs)
                tasks.append(record.save())
                tasks.append(kwargs['parent'].save())
        await asyncio.gather(*tasks)


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
    old = TextField(null=True)
    new = TextField(null=True)
    column = TextField()
    req_guid = UUIDField(unique=False)

    class Meta:
        app = "erot"


__models__ = [
    Base, Description, Compliance, Liability, Sanction, Control, Attribute,
    Updates
]

__all__ = ['Base', 'Description', 'Compliance', 'Liability', 'Sanction', 'Control', 'Attribute',
    'Updates']