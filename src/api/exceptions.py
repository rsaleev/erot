


class DocumentValidationError(Exception):
    pass


class DocumentSchemaNotFound(DocumentValidationError):
    pass


class DocumentIntegrityError(DocumentValidationError):
    pass

class FormatError(Exception):
    pass


class DateFormatError(FormatError):
    pass 


class LoaderError(Exception):
    pass
class ExtractorError(Exception):
    pass

class ExcelExtractorError(ExtractorError):
    pass

class WorkbookNotFound(ExcelExtractorError):
    pass

class SheetNotFound(ExcelExtractorError):
    pass

class SheetNotValid(ExcelExtractorError):
    pass

class SheetValidationError(ExcelExtractorError):
    pass


class MappingNotFound(ExcelExtractorError):
    pass