"""
Модуль для обработки PDF-файлов с планами лечения.
Извлекает текстовое содержимое из PDF и определяет тип документа.
"""

from typing import Dict, Any, Optional
from enum import Enum
import fitz  # PyMuPDF
from pathlib import Path


class ProcessingStatus(str, Enum):
    """Статусы обработки PDF-документа"""
    SUCCESS = "success"
    PROCESS = "process"
    ERROR = "error"


class PDFProcessorResponse:
    """Класс для формирования ответа обработчика PDF"""

    def __init__(self, status: ProcessingStatus, message: str, data: Optional[Dict[str, Any]] = None):
        self.status = status
        self.message = message
        self.data = data or {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование ответа в словарь"""
        return {
            "status": self.status.value,
            "message": self.message,
            "data": self.data
        }


class PDFProcessor:
    """Обработчик PDF-документов с планами лечения"""

    # Пороговое значение для определения, является ли PDF картинкой
    MIN_TEXT_LENGTH = 50  # Минимальное количество символов на странице
    MIN_TEXT_RATIO = 0.1  # Минимальное соотношение текстовых символов к общему объему

    def __init__(self, pdf_path: str):
        """
        Инициализация обработчика

        Args:
            pdf_path: Путь к PDF-файлу
        """
        self.pdf_path = Path(pdf_path)
        self.doc = None

    def _open_pdf(self) -> PDFProcessorResponse:
        """Открытие PDF-файла"""
        try:
            if not self.pdf_path.exists():
                return PDFProcessorResponse(
                    status=ProcessingStatus.ERROR,
                    message=f"Файл не найден: {self.pdf_path}"
                )

            if not self.pdf_path.suffix.lower() == '.pdf':
                return PDFProcessorResponse(
                    status=ProcessingStatus.ERROR,
                    message=f"Файл должен быть в формате PDF, получен: {self.pdf_path.suffix}"
                )

            self.doc = fitz.open(self.pdf_path)
            return PDFProcessorResponse(
                status=ProcessingStatus.SUCCESS,
                message="PDF-файл успешно открыт"
            )
        except Exception as e:
            return PDFProcessorResponse(
                status=ProcessingStatus.ERROR,
                message=f"Ошибка при открытии PDF-файла: {str(e)}"
            )

    def _is_image_based_pdf(self) -> bool:
        """
        Определение, является ли PDF картинкой (требует OCR)

        Returns:
            True, если PDF является картинкой, False - если структурированный
        """
        if not self.doc:
            return True

        total_text_length = 0
        total_pages = len(self.doc)

        # Проверяем все страницы
        for page_num in range(total_pages):
            page = self.doc[page_num]
            text = page.get_text().strip()

            # Убираем пробелы и переносы строк для более точного подсчета
            text_without_spaces = ''.join(text.split())
            total_text_length += len(text_without_spaces)

        # Если на всех страницах очень мало текста, скорее всего это картинка
        avg_text_per_page = total_text_length / total_pages if total_pages > 0 else 0

        # Также проверяем наличие изображений
        has_images = False
        for page_num in range(min(3, total_pages)):  # Проверяем первые 3 страницы
            page = self.doc[page_num]
            image_list = page.get_images()
            if image_list:
                has_images = True
                break

        # Если много изображений и мало текста - это картинка
        if has_images and avg_text_per_page < self.MIN_TEXT_LENGTH:
            return True

        # Если очень мало текста - это картинка
        if avg_text_per_page < self.MIN_TEXT_LENGTH:
            return True

        return False

    def _extract_text(self) -> str:
        """
        Извлечение текста из PDF-документа

        Returns:
            Извлеченный текст из всех страниц
        """
        if not self.doc:
            return ""

        all_text = []
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            all_text.append(f"--- Страница {page_num + 1} ---\n{text}")

        return "\n\n".join(all_text)

    def _get_metadata(self) -> Dict[str, Any]:
        """
        Извлечение метаданных из PDF

        Returns:
            Словарь с метаданными документа
        """
        if not self.doc:
            return {}

        metadata = self.doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "pages_count": len(self.doc)
        }

    def process(self) -> Dict[str, Any]:
        """
        Основная функция обработки PDF-файла

        Returns:
            Словарь с результатами обработки
        """
        # Открываем PDF
        open_result = self._open_pdf()
        if open_result.status == ProcessingStatus.ERROR:
            return open_result.to_dict()

        try:
            # Проверяем, является ли PDF картинкой
            if self._is_image_based_pdf():
                return PDFProcessorResponse(
                    status=ProcessingStatus.ERROR,
                    message="Переданный PDF-файл является картинкой и требует OCR. "
                            "Пока не умею работать с таким форматом.",
                    data={
                        "pdf_type": "image_based",
                        "requires_ocr": True,
                        "metadata": self._get_metadata()
                    }
                ).to_dict()

            # Извлекаем текст
            extracted_text = self._extract_text()

            if not extracted_text.strip():
                return PDFProcessorResponse(
                    status=ProcessingStatus.ERROR,
                    message="Не удалось извлечь текст из PDF-файла. Возможно, файл поврежден или зашифрован.",
                    data={"metadata": self._get_metadata()}
                ).to_dict()

            # Успешная обработка
            return PDFProcessorResponse(
                status=ProcessingStatus.SUCCESS,
                message="PDF-файл успешно обработан",
                data={
                    "pdf_type": "structured",
                    "text": extracted_text,
                    "metadata": self._get_metadata(),
                    "text_length": len(extracted_text)
                }
            ).to_dict()

        except Exception as e:
            return PDFProcessorResponse(
                status=ProcessingStatus.ERROR,
                message=f"Ошибка при обработке PDF-файла: {str(e)}"
            ).to_dict()

        finally:
            # Закрываем документ
            if self.doc:
                self.doc.close()


def process_treatment_plan_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Функция-обертка для обработки PDF с планом лечения

    Args:
        pdf_path: Путь к PDF-файлу с планом лечения

    Returns:
        Словарь с результатами обработки:
        {
            "status": "success" | "process" | "error",
            "message": "Техническое сообщение",
            "data": {
                "pdf_type": "structured" | "image_based",
                "text": "Извлеченный текст",
                "metadata": {...},
                ...
            }
        }

    Example:
        >>> result = process_treatment_plan_pdf("/path/to/plan.pdf")
        >>> if result["status"] == "success":
        >>>     print(result["data"]["text"])
        >>> else:
        >>>     print(result["message"])
    """
    processor = PDFProcessor(pdf_path)
    return processor.process()