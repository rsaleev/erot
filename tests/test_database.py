import os
import pytest

import asyncio


from tortoise import Tortoise

from src.database.models.erot import Base, Compliance, Description, ErotModel, Liability

from datetime import datetime

from uuid import UUID


@pytest.mark.asyncio
async def init_db() -> None:

    from src.config.database import CONFIG
    """Initial database connection"""
    await Tortoise.init(config=CONFIG)

    await Tortoise.generate_schemas()
    print("Success to generate schemas")


@pytest.mark.asyncio
@pytest.fixture(scope="module")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="module", autouse=True)
async def initialize_tests():
    await init_db()
    yield
    #await Tortoise._drop_databases()
    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_base():
    record = await Base.get_or_none(id=1)
    assert record


@pytest.mark.asyncio
async def test_description():
    base = await Base.get_or_none(id=1)
    data = {
        'desc_validity_status': None,
        'desc_valid_to': datetime(2025, 12, 31),
        'desc_act_text':
        '4. За работающими гражданами, вызываемыми в арбитражный суд в качестве свидетелей, сохраняется средний заработок по месту их работы за время отсутствия в связи с явкой их в суд. Свидетели, не состоящие в трудовых отношениях, за отвлечение их от обычных занятий получают компенсацию с учетом фактически затраченного времени. Порядок и размерывыплаты данной компенсации устанавливаются Правительством Российской Федерации',
        'desc_act_requisites': ['Часть: 4', 'Статья: 107.'],
        'desc_regulation_level': 1,
        'desc_work_status': 0,
        'desc_publication_date': None,
        'desc_publication_status': 5,
        'req_guid_id': UUID('4662863f14914ff4a25aaaf42295e147')
    }
    record = await Description.get_or_none(req_guid_id=base.req_guid)
    assert record
    data['desc_publication_status']=6
    await Description.create_or_update(**data)


@pytest.mark.asyncio
async def test_compliance():
    record = await Compliance.get_or_none(id=1)
    assert record


@pytest.mark.asyncio
async def test_liability():
    kwargs = {
        'lblt_subjects': [1, 2],
        'lblt_organization':
        None,
        'lblt_act_text':
        '1. Нарушение трудового законодательства и иных нормативных правовых актов, содержащих нормы трудового права, если иное не предусмотрено частями 3, 4 и 6 настоящей статьи и статьей 5.27.1 настоящего Кодекса, - влечет предупреждение или наложение административного штрафа на должностных лиц в размере от одной тысячи до пяти тысяч рублей; на лиц, осуществляющих предпринимательскую деятельность без образования юридического лица, - от одной тысячи до пяти тысяч рублей; на юридических лиц - от тридцати тысяч до пятидесяти тысяч рублей. 2. Совершение административного правонарушения, предусмотренного частью 1 настоящей статьи, лицом, ранее подвергнутым административному наказанию за аналогичное административное правонарушение, - влечет наложение административного штрафа на должностных лиц в размере от десяти тысяч до двадцати тысяч рублей или дисквалификацию на срок от одного года до трех лет; на лиц, осуществляющих предпринимательскую деятельность без образования юридического лица, - от десяти тысяч до двадцати тысяч рублей; на юридических лиц - от пятидесяти тысяч до семидесяти тысяч рублей.\n6. Невыплата или неполная выплата в установленный срок заработной платы, других выплат, осуществляемых в рамках трудовых отношений, если эти действия не содержат уголовно наказуемого деяния, либо воспрепятствование работодателем осуществлению работником права на замену кредитной организации, в которую должна быть переведена заработная плата, либо установление заработной платы в размере менее размера, предусмотренного трудовым законодательством, - влечет предупреждение или наложение административного штрафа на должностных лиц в размере от десяти тысяч до двадцати тысяч рублей; на лиц, осуществляющих предпринимательскую деятельность без образования юридического лица, - от одной тысячи до пяти тысяч рублей; на юридических лиц - от тридцати тысяч до пятидесяти тысяч рублей. 7. Совершение административного правонарушения, предусмотренного частью 6 настоящей статьи, лицом, ранее подвергнутым административному наказанию за аналогичное правонарушение, если эти действия не содержат уголовно наказуемого деяния, - влечет наложение административного штрафа на должностных лиц в размере от двадцати тысяч до тридцати тысяч рублей или дисквалификацию на срок от одного года до трех лет; на лиц, осуществляющих предпринимательскую деятельность без образования юридического лица, - от десяти тысяч до тридцати тысяч рублей; на юридических лиц - от пятидесяти тысяч до ста тысяч рублей.',
        'lblt_act_clause':
        'Часть 1 или 2, 6 или 7 статьи 5.27 КоАП РФ',
        'lblt_act_article':
        'статьи 5.27 КоАП РФ',
        'lblt_act_title':
        'Кодекс Российской Федерации об административных правонарушениях',
    }
    base = await Base.get_or_none(id=1)
    await Liability.create_or_update(**kwargs, req_guid_id=base.req_guid)
   

@pytest.mark.asyncio 
async def test_sanction():
    assert True
