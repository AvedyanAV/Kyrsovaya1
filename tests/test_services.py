import pandas as pd
from unittest.mock import patch
from src.services import person_transfers


def test_valid_person_transfers():
    """Тест корректного перевода физлицам"""
    test_data = pd.DataFrame({
        'Категория': ['Переводы', 'Переводы', 'Покупки'],
        'Описание': ['Иванов А. Перевод', 'Петрова М. За услуги', 'Магазин'],
        'Сумма операции': [1000, 2000, 500],
        'Дата операции': ['2023-01-01', '2023-01-02', '2023-01-03']
    })

    with patch('pandas.read_excel', return_value=test_data):
        result = person_transfers()

        assert len(result) == 2
        assert result[0]['recipient'] == 'Иванов'
        assert result[0]['amount'] == 1000.0
        assert result[0]['description'] == 'Иванов А. Перевод'

        assert result[1]['recipient'] == 'Петрова'
        assert result[1]['amount'] == 2000.0


def test_empty_dataframe():
    """Тест пустого DataFrame"""
    test_data = pd.DataFrame(columns=['Категория', 'Описание', 'Сумма операции', 'Дата операции'])

    with patch('pandas.read_excel', return_value=test_data):
        result = person_transfers()
        assert result == []


def test_nan_date_handling():
    """Тест обработки отсутствующей даты"""
    test_data = pd.DataFrame({
        'Категория': ['Переводы'],
        'Описание': ['Иванов А. Перевод'],
        'Сумма операции': [1000],
        'Дата операции': [pd.NaT]
    })

    with patch('pandas.read_excel', return_value=test_data):
        result = person_transfers()

        assert len(result) == 1
        assert result[0]['date'] == "Не указана"
