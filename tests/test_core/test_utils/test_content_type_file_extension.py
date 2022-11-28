import unittest

from askanna.core.utils.file import content_type_file_extension


class ContentTypeFileExtension(unittest.TestCase):
    def test_csv(self):
        content_type = "application/csv"
        self.assertEqual(content_type_file_extension(content_type), ".csv")

    def test_json(self):
        content_type = "application/json"
        self.assertEqual(content_type_file_extension(content_type), ".json")

    def test_xls(self):
        content_type = "application/vnd.ms-excel"
        self.assertEqual(content_type_file_extension(content_type), ".xls")

    def test_xlsx(self):
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        self.assertEqual(content_type_file_extension(content_type), ".xlsx")

    def test_zip(self):
        content_type = "application/zip"
        self.assertEqual(content_type_file_extension(content_type), ".zip")

    def test_jpeg(self):
        content_type = "image/jpeg"
        self.assertEqual(content_type_file_extension(content_type), ".jpeg")

    def test_png(self):
        content_type = "image/png"
        self.assertEqual(content_type_file_extension(content_type), ".png")

    def test_txt(self):
        content_type = "text/plain"
        self.assertEqual(content_type_file_extension(content_type), ".txt")

    def test_xml(self):
        content_type = "text/xml"
        self.assertEqual(content_type_file_extension(content_type), ".xml")

    def test_octet_stream(self):
        content_type = "application/octet-stream"
        self.assertEqual(content_type_file_extension(content_type), ".unknown")

    def test_unknown(self):
        content_type = "unknown"
        self.assertEqual(content_type_file_extension(content_type), ".unknown")
