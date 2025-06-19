import os
import re
import io
import logging
from typing import List, Optional, Tuple

import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Element
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/test_data/parser.log'),
        logging.StreamHandler()
    ]
)

# Конфигурация логгера
logger = logging.getLogger(__name__)

# Конфигурация Tesseract OCR
try:
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    TESSDATA_PATH = r'C:\Program Files\Tesseract-OCR\tessdata'
    
    if os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        os.environ['TESSDATA_PREFIX'] = TESSDATA_PATH
    else:
        logger.error("Tesseract not found at %s", TESSERACT_PATH)
        raise RuntimeError(_("Tesseract OCR не установлен или путь указан неверно"))
except Exception as e:
    logger.critical("Tesseract configuration failed: %s", str(e))
    raise


class FileProcessor:
    """Класс для обработки загружаемых файлов анализов"""
    
    SUPPORTED_IMAGE_TYPES = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    SUPPORTED_PDF_TYPE = '.pdf'
    
    @classmethod
    def extract_text(cls, file) -> str:
        """
        Извлекает текст из файла (PDF или изображения)
        
        Args:
            file: UploadedFile object
            
        Returns:
            str: Извлеченный текст
            
        Raises:
            ValidationError: Если файл не поддерживается или произошла ошибка обработки
        """
        try:
            if file.name.lower().endswith(cls.SUPPORTED_PDF_TYPE):
                return cls._process_pdf(file)
            elif file.name.lower().endswith(cls.SUPPORTED_IMAGE_TYPES):
                return cls._process_image(file)
            else:
                raise ValidationError(_("Неподдерживаемый формат файла. Поддерживаются PDF и изображения."))
        except Exception as e:
            logger.error("File processing error: %s", str(e))
            raise ValidationError(_("Ошибка обработки файла: {}").format(str(e)))

    @staticmethod
    def _process_pdf(file) -> str:
        """Обработка PDF файлов"""
        text = ""
        try:
            # Попытка извлечь текст напрямую из PDF
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            
            # Если текст не извлекся, используем OCR
            if not text.strip():
                images = convert_from_bytes(file.read(), dpi=300)
                for img in images:
                    text += pytesseract.image_to_string(img) + "\n"
        
        except Exception as e:
            logger.error("PDF processing error: %s", str(e))
            raise ValidationError(_("Ошибка обработки PDF файла"))
        
        return text.strip()

    @staticmethod
    def _process_image(file) -> str:
        """Обработка изображений"""
        try:
            img = Image.open(file)
            return pytesseract.image_to_string(img)
        except UnidentifiedImageError:
            raise ValidationError(_("Неподдерживаемый формат изображения"))
        except Exception as e:
            logger.error("Image processing error: %s", str(e))
            raise ValidationError(_("Ошибка обработки изображения"))


class AnalysisParser:
    """Класс для анализа текста и рекомендации элементов"""
    
    ELEMENT_PATTERNS = {
        'витамин d': (r'витамин\s*[dд][\s:-]*(\d+\.?\d*)', 30, 100),
        'железо': (r'железо[\s:-]*(\d+\.?\d*)', 10, 30),
        'магний': (r'магни\w+[\s:-]*(\d+\.?\d*)', 0.7, 1.1),
        'витамин b12': (r'витамин\s*b\s*12[\s:-]*(\d+\.?\d*)', 200, 900),
        'фолиевая кислота': (r'фолиев\w+\s*кислот\w+[\s:-]*(\d+\.?\d*)', 4, 20),
    }
    
    @classmethod
    def recommend_elements(cls, text: str) -> List[Element]:
        """
        Анализирует текст и рекомендует элементы на основе значений анализов
        
        Args:
            text: Текст из анализов
            
        Returns:
            List[Element]: Список рекомендованных элементов
        """
        if not text:
            return []
        
        recommended = []
        
        for name, (pattern, min_val, max_val) in cls.ELEMENT_PATTERNS.items():
            try:
                elements = cls._process_element_pattern(text, name, pattern, min_val, max_val)
                recommended.extend(elements)
            except Exception as e:
                logger.error("Error processing element %s: %s", name, str(e))
                continue
        
        # Удаляем дубликаты
        seen = set()
        return [x for x in recommended if not (x.id in seen or seen.add(x.id))]
    
    @staticmethod
    def _process_element_pattern(text: str, name: str, pattern: str, 
                               min_val: float, max_val: float) -> List[Element]:
        """Обрабатывает шаблон для конкретного элемента"""
        elements = []
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            try:
                value = float(match.group(1).replace(',', '.'))
                element = Element.objects.filter(name__icontains=name).first()
                
                if element:
                    elem_min = element.min_normal_value if element.min_normal_value is not None else min_val
                    elem_max = element.max_normal_value if element.max_normal_value is not None else max_val
                    
                    if not (elem_min <= value <= elem_max):
                        elements.append(element)
                        logger.info("Recommended %s (value: %s)", name, value)
            except (ValueError, AttributeError) as e:
                logger.warning("Value conversion error for %s: %s", name, str(e))
                continue
        
        return elements


# Функции для обратной совместимости
def extract_text_from_file(file):
    return FileProcessor.extract_text(file)

def recommend_elements_from_text(text):
    return AnalysisParser.recommend_elements(text)