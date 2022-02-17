import pytest 

from pathlib import Path

from src.api.extractors.excel import ExcelExtractor
from src.api.base.objects import Object, Attribute


import os

@pytest.fixture(scope="session", autouse=True)
def tests_setup_and_teardown():

    os.environ['TEST_DIR'] = os.path.dirname(os.path.abspath(__file__))
    os.environ['VALIDATION_URL'] = 'http://127.0.0.1:8000/documents/validate'

    os.environ['SHEET_MAX_COL']='100'
    os.environ['SHEET_MAX_ROW']='200'

    # yield
    # os.environ.clear()



def test_read_workbook():
    extractor = ExcelExtractor()
    filename = str(Path(f'{os.environ["TEST_DIR"]}/Реестр_обязательных_требований_21.xlsx'))
    extractor.read(filename)
    assert extractor.workbook

@pytest.mark.asyncio
async def test_read_and_validate():
    extractor = ExcelExtractor()
    filename = str(Path(f'{os.environ["TEST_DIR"]}/Реестр_обязательных_требований_21.xlsx'))
    extractor.read(filename)
    assert extractor.workbook
    await extractor.validate()
    assert extractor.worksheet
    object = extractor.extract()
    assert object
    assert object.attributes
    assert all([isinstance(attr, Attribute) for attr in object.attributes])
    for attr in object.attributes:
        if attr.document.format:
            for fmt in attr.document.format:
                assert fmt._instance

            