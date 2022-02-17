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
    