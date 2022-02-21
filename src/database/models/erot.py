from typing import Union, List, Any, Tuple

from anyio import wait_all_tasks_blocked

from tortoise.fields import (CharField, DatetimeField, DateField, TextField,
                             UUIDField, ReverseRelation, IntField,
                             OneToOneField, ForeignKeyField)
from tortoise.models import Model

from tortoise.queryset import QuerySetSingle, QuerySet

from src.database.custom_fields import NumericArrayField, TextArrayField

from src.database.helpers import kwargs_to_pg_types, compare_records, model_to_dict

import asyncio

import re

class ErotModel(Model):

    @classmethod
    def _get_fk(cls):
        return [
            name for name, field in cls._meta.fields_map.items()
            if name in cls._meta.fk_fields
        ]

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
        if cls._get_fk():
            raise NotImplementedError(
                "Метод не предназначен для родительской записи")
        tasks = []
        record = await super().get_or_none(req_guid_id=kwargs['req_guid_id'])
        if not record:
            tasks.append(super().create(**kwargs))
        else:
            record_values = model_to_dict(record)
            if diffs := compare_records(record_values, kwargs):
                tasks.append(
                    Updates.bulk_create([
                        Updates(**diff, req_guid=kwargs['req_guid_id'])
                        for diff in diffs
                    ]))
                record.update_from_dict(kwargs)
                tasks.append(record.save())
                parent = await Base.get(req_guid=kwargs['req_guid_id'])
                tasks.append(parent.save())
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
    cmpl_act_type = IntField(null=False)
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


class Sanction(ErotModel):
    id = IntField(pk=True)
    snct_subject = IntField(null=False)
    snct_title = TextField(null=True)
    snct_content = TextField(null=True)
    snct_min = IntField(null=True)
    snct_max = IntField(null=True)
    snct_measure = TextField(null=True)
    snct_comments = TextField(null=True)

    req_guid = ForeignKeyField('erot.Base',
                               to_field='req_guid',
                               related_name='sanctions')

    @classmethod
    async def create_or_update(cls, **kwargs):
        """
        Sanction.create(cls, **kwargs)

        перезагрузка метода для создания одиночных записей, если в значениях указаны несколько субъектов
        """
        tasks = []
        # разбор массива значений на единичные словари
        for title in kwargs['snct_title']:
            # создание пустого словаря
            single_data = {}
            # назначение типа субъекта
            single_data['snct_subject'] = kwargs['snct_subject']
            # назначение типа санкциии
            single_data['snct_title'] = title
            record = await cls.get_or_none(req_guid_id=kwargs['req_guid_id'],
                                           snct_title=title,
                                           snct_subject=kwargs['snct_subject'])
            # мэппинг соотвутствующей санкции:
            # Административный штраф: от 1000 до 5000 (в рублях)
            content = next(
                (c.replace(title, '').replace(':', '').strip()
                 for c in kwargs['snct_content'] if c.rfind(title) > -1), None)
            single_data['snct_content'] = content
            if kwargs['snct_comments']:
                single_data['snct_comments'] = next(
                    (c.replace(title, '').replace(':', '').strip()
                    for c in kwargs['snct_comments'] if c.rfind(title) > -1),
                    None)
            # парсинг санкции с разбором на минимальное значение/максимальное и тип калькуляции
            if content:
                content_measures = re.match(r"^(?<min>от\s*(?<min_val>\d+))|.*(?<max>до\s*(?<max_val>\d+))|.*(?<measure>\(...*\))$", content)
                if not content_measures:
                    raise ValueError
                single_data['snct_min'] = content_measures.groupdict('min')
                single_data['snct_max'] = content_measures.groupdict('max')
                single_data['snct_measure'] = content_measures.groupdict('measure')
            single_data.update(kwargs['req_guid_id'])
            if record:
                if record.snct_min != single_data['snct_min']:
                    record.update_from_dict({'snct_min':single_data['snct_min']})
                    tasks.append(Updates.create(old=record.snct_min, new=single_data['snct_min'], column='snct_min'))
                if record.snct_max !=  single_data['snct_max']:
                    record.update_from_dict({'snct_max':single_data['snct_max']})
                    tasks.append(Updates.create(old=record.snct_max, new=single_data['snct_max'], column='snct_max'))
                if record.snct_measure !=  single_data['snct_measure']:
                    record.update_from_dict({'snct_measure':single_data['snct_measure']})
                    tasks.append(Updates.create(old=record.snct_measure, new=single_data['snct_measure'], column='snct_measure'))
                tasks.append(record.save())
            else:
                tasks.append(super().create(**single_data))
        await asyncio.gather(*tasks)

    # @classmethod
    # async def get_or_none(cls, **kwargs):
    #     tasks = []
    #     if kwargs['snct_title']:
    #         for title in kwargs['snct_title']:
    #             single_data = {}
    #             single_data['snct_subject'] = kwargs['snct_subject']
    #             single_data['snct_title'] = title
    #             single_data['snct_content'] = next(
    #                 (c.replace(title, '').replace(':', '').strip()
    #                  for c in kwargs['snct_content'] if c.rfind(title) > -1),
    #                 None)
    #             if kwargs['snct_comments']:
    #                 single_data['snct_comments'] = next(
    #                     (c.replace(title, '').replace(':', '').strip()
    #                      for c in kwargs['snct_comments']
    #                      if c.rfind(title) > -1), None)
    #             single_data.update({'req_guid_id': kwargs['req_guid_id']})
    #             tasks.append(super().get_or_none(**single_data))
    #         return await asyncio.gather(*tasks)
    #     return

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
