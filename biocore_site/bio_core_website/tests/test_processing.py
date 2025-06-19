import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from bio_core_website.utils import extract_text_from_file, recommend_elements_from_text

class FileProcessingTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем тестовый PDF-контент (только ASCII символы)
        cls.pdf_content_ru = (
            "БИОХИМИЧЕСКИЙ АНАЛИЗ\n"
            "Показатель|Результат|Норма\n"
            "Витамин D|18 нг/мл|30-100\n"
            "Железо|8.5 мкмоль/л|9-30"
        ).encode('utf-8')

    def test_pdf_processing_ascii(self):
        file = SimpleUploadedFile(
            "test.pdf",
            self.pdf_content,
            content_type="application/pdf"
        )
        text = extract_text_from_file(file)
        self.assertIn("Vitamin D", text)
        
        recommendations = recommend_elements_from_text(text)
        self.assertTrue(any('vitamin d' in elem.name.lower() for elem in recommendations))

    def test_pdf_processing_unicode(self):
        file = SimpleUploadedFile(
            "test_ru.pdf",
            self.pdf_content_ru,
            content_type="application/pdf"
        )
        text = extract_text_from_file(file)
        self.assertIn("Витамин D", text)
        
        recommendations = recommend_elements_from_text(text)
        self.assertTrue(any('витамин d' in elem.name.lower() for elem in recommendations))