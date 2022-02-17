from typing import Union

import os

from aiohttp import ClientSession


from openpyxl import Workbook, load_workbook
from openpyxl.worksheet._read_only import ReadOnlyWorksheet
from openpyxl.worksheet.worksheet import Worksheet

from src.api.base.extractor import DocumentExtractor
from src.api.base.objects import Object
from src.api.base.schema import DocumentSchemaResponse, Header
from src.api.exceptions import SheetValidationError, WorkbookNotFound


class ExcelExtractor(DocumentExtractor):

    __slots__ = ('workbook', 'worksheet', '_min_row', '_max_row', '_min_col',
                 '_max_col', '_document', '_header', '_sheetname')

    def __init__(self):
        self.workbook: Workbook
        self.worksheet: Union[Worksheet, ReadOnlyWorksheet]
        self._min_row = 1
        self._max_row = int(os.environ['SHEET_MAX_ROW'])
        self._min_col = 1
        self._max_col = int(os.environ['SHEET_MAX_COL'])
        self._document: Object
        self._header: Union[Header, None]

    def read(self, filename: str):
        """
        read 

        Загрузка файла/рабочей книги

        Args:
            filename (str): имя файла/путь

        Raises:
            WorkbookNotFound: рабочая книга/файл не найден по указанному пути
        """
        # открытие книги/файла
        try:
            self.workbook = load_workbook(filename,
                                          read_only=True,
                                          keep_vba=False,
                                          data_only=True,
                                          keep_links=False)
        except:
            raise WorkbookNotFound(f'Файл {filename} не найден')

    async def _send_validation_request(self,
                                       row: tuple) -> DocumentSchemaResponse:
        # генерация query params
        # headers=Заголовок1&headers=Заголовок2&...
        params = '&'.join([
            f'headers={cell.value}' for cell in row
            if cell.value and cell.value != '' and cell.value is not None
        ])
        if not params:
            return DocumentSchemaResponse(error='Пустой заголовок', data=None)
        # отправка запроса
        async with ClientSession() as session:
            async with session.get(url=os.environ['VALIDATION_URL'],
                                params=params) as r:
                response = DocumentSchemaResponse(**await r.json())
                return response

    def _set_document(self, response: DocumentSchemaResponse):
        # инициализация структуры
        if not response.data:
            return
        self._document = Object(response.data.name) 
        [self._document.add_field(column) for column in response.data.columns]

    def _set_header(self, response: DocumentSchemaResponse):
        # установка заголовка документа
        if response.data and response.data.header:
            self._header = response.data.header

    def _set_dimensions(self, row):
        """
        Определение размерности документа

        Args:
            row ([type]): [description]
        """
        # минимальная строка -> индекс строки с заголовком + 1 строка вниз
        self._min_row = row[0].row + 1
        self._max_col = max(col.document.index
                            for col in self._document.attributes)
        for row in self.worksheet.iter_rows(min_row=self._min_row,
                                            min_col=1,
                                            max_col=1,
                                            max_row=self._max_row):
            try:
                self._max_row = row[0].row
            except AttributeError:
                break

    async def validate(self):
        """
        Проверка первых 10 строк на соответствие схемам заголовков документов

        Raises:
            SheetNotValid: при окончании итерации и отсутствии совпадения (включая отсутствующие обязательные заголовки столбцов)
        """
        error = 'Не удалось соотнести структуру документа и схему'
        valid = False
        for sheet in self.workbook.sheetnames:
            ws = self.workbook[sheet]
            if not isinstance(ws, (ReadOnlyWorksheet, Worksheet)):
                continue
            for row in ws.iter_rows(min_row=1,
                                    max_row=10,
                                    max_col=self._max_col):
                response = await self._send_validation_request(row)
                if response.error:
                    error = response.error
                    continue
                elif response.data:
                    valid = True
                    # назначение рабочего листа
                    self.worksheet = ws
                    # назначение структуры документа
                    self._set_document(response)
                    self._set_header(response)
                    self._set_dimensions(row)
                    break
        if not valid:
            raise SheetValidationError(error)
    
    def extract(self) -> Object:
        """
        extract 

        [extended_summary]

        Raises:
            StopIteration
        Returns:
            Object: [description]
        """
        if self._min_row <= self._max_row:
            # выборка одной строки из рабочего листа
            row = next(
                row for row in self.worksheet.iter_rows(min_row=self._min_row,
                                                        max_row=self._max_row,
                                                        min_col=self._min_col,
                                                        max_col=self._max_col,
                                                        values_only=True))
            # преобразование в объект с атрибутами
            doc_object = self._document.get_copy()
            for attribute in doc_object.attributes:
                # определение значений по индексу, co смещением на 1
                attribute.value = row[attribute.document.index-1]          
            # увеличение текущего индекса строки
            self._min_row = +1
            return doc_object
        else:
            self.workbook.close()
            raise StopIteration('Exhausted')
