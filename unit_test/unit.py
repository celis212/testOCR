from classes.ocr import Ocr
from unittest import mock

def ocr():
  return Ocr()

# Test the get_data method
def test_generate_id():
  ocr = Ocr()
  file_name = "img/test.jpg"
  expected_result = "d8e8fca2dc0f896fd7cb4cb0031ba249"
  assert ocr.generate_id(file_name) == expected_result