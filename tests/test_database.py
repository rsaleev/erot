import os
from celery import uuid 
import pytest

import asyncio

from uuid import uuid4

from tortoise.contrib.test import finalizer, initializer

from tests.test_models import User, Role




@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    initializer(["tests.test_models"], db_url="sqlite://:memory:", app_label="models")
    print('initialzing')
    request.addfinalizer(finalizer())
    
@pytest.mark.asyncio
async def test_user_get_or_none_values():
    user_new = User(firstname='Jane', lastname='Doe')
    await user_new.save()
    user_record = await User.get_or_none(id=1).values()
    assert isinstance(user_record, dict)
    assert user_record.__getitem__('firstname') == 'Jane' #type: ignore
    assert user_record.__getitem__('lastname') == 'Doe' #type: ignore

# async def test_user_get_or_create():
#     values = {'firstname':'Jane', 'lastname':'Doe'}
#     user_record = await test_models.User.get_or_none(**values)
#     assert user_record == None
#     await test_models.User.create(**values)
#     user_record_check = await test_models.User.get_or_none(**values)
#     assert user_record_check != None

# async def test_bulk_user_create():
#     values = [{'firstname':'Jane', 'lastname':'Doe'}, {'firstname':'John', 'lastname':'Doe'}]
#     await test_models.User.bulk_create([test_models.User(**v) for v in values])
#     result = await test_models.User.all()
#     assert isinstance(list(result), list)
#     assert len(result) >0

# async def test_relation():
#     role = await test_models.Role.create(title='manager', guid=uuid4())
#     assert role
#     user = await test_models.User.create(firstname='Jack', lastname='Daniels', role=role)
#     assert user
#     roles = await test_models.Role.all().prefetch_related('users')
#     assert roles
    