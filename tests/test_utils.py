import json
import logging
from src.utils import greeting, cards, stock_prices
import pytest
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd


def test_json_read_success(tmp_path):
    """Тест успешного чтения корректного JSON файла"""
    from src.utils import json_read

    test_data = {"currency": ["USD", "EUR"], "stocks": ["AAPL", "GOOGL"]}
    test_file = tmp_path / "user_settings.json"
    test_file.write_text(json.dumps(test_data), encoding='utf-8')

    with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
        with patch('src.utils.json_read.__defaults__', (str(test_file),)):
            result = json_read()

    assert result == test_data


def test_json_read_file_not_found(caplog):
    """Тест обработки отсутствующего файла"""
    from src.utils import json_read

    with patch('builtins.open') as mock_open:
        mock_open.side_effect = FileNotFoundError("File not found")
        with caplog.at_level(logging.ERROR):
            result = json_read()

    assert result == {}
    assert "Файл data/user_settings.json не найден" in caplog.text


def test_json_read_json_decode_error(tmp_path, caplog):
    """Тест обработки некорректного JSON"""
    from src.utils import json_read

    test_file = tmp_path / "user_settings.json"
    test_file.write_text("{invalid json}", encoding='utf-8')

    def mock_file_open(*args, **kwargs):
        return test_file.open('r', encoding='utf-8')

    with patch('builtins.open', mock_file_open):
        with caplog.at_level(logging.ERROR):
            result = json_read()

    assert result == {}
    assert "Ошибка при чтении JSON файла" in caplog.text


def test_json_read_empty_file(tmp_path):
    """Тест чтения пустого файла"""
    from src.utils import json_read

    test_file = tmp_path / "user_settings.json"
    test_file.write_text("", encoding='utf-8')

    def mock_file_open(*args, **kwargs):
        return test_file.open('r', encoding='utf-8')

    with patch('builtins.open', mock_file_open):
        result = json_read()

    assert result == {}


@patch('src.utils.datetime.datetime')
def test_greeting_boundary_cases(mock_datetime):
    """Тест граничных случаев"""

    mock_now = mock_datetime.now.return_value
    mock_now.hour = 6
    assert greeting() == "Доброе утро"

    mock_now.hour = 10
    assert greeting() == "Добрый день"

    mock_now.hour = 18
    assert greeting() == "Добрый вечер"

    mock_now.hour = 22
    assert greeting() == "Доброй ночи"


@patch('src.utils.pd.read_excel')
def test_cards_basic_functionality(mock_read_excel):
    """Тест базовой функциональности"""
    test_data = {
        'Номер карты': ['1234567890123456', '9876543210987654', '1234567890123456'],
        'Сумма операции': [-100.0, -200.0, -50.0]
    }
    df = pd.DataFrame(test_data)
    mock_read_excel.return_value = df

    result = cards()

    assert '3456' in result
    assert '7654' in result
    assert result['3456']['total_spent'] == 150.0
    assert result['3456']['cashback'] == 1.0
    assert result['7654']['total_spent'] == 200.0
    assert result['7654']['cashback'] == 2.0


@patch('src.utils.pd.read_excel')
def test_cards_file_not_found(mock_read_excel):
    """Тест обработки отсутствующего файла"""
    mock_read_excel.side_effect = FileNotFoundError("File not found")

    result = cards()
    assert result == {}


@patch('src.utils.pd.read_excel')
def test_cards_missing_columns(mock_read_excel):
    """Тест обработки отсутствующих колонок"""
    test_data = {'Другая колонка': [1, 2, 3]}
    df = pd.DataFrame(test_data)
    mock_read_excel.return_value = df

    result = cards()
    assert result == {}


def test_top_transactions_success():
    """Тест успешного выполнения функции с корректными данными"""
    test_data = {
        'Дата платежа': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06'],
        'Сумма операции с округлением': [1000.0, 5000.0, 3000.0, 7000.0, 2000.0, 9000.0],
        'Категория': ['Еда', 'Транспорт', 'Развлечения', 'Еда', 'Транспорт', 'Развлечения'],
        'Описание': ['Обед', 'Такси', 'Кино', 'Ужин', 'Метро', 'Концерт']
    }

    df = pd.DataFrame(test_data)

    with patch('pandas.read_excel') as mock_read_excel, \
            patch('logging.error') as mock_logging:
        mock_read_excel.return_value = df

        from src.utils import top_transactions
        result = top_transactions()

        assert len(result) == 5

        amounts = [item['amount'] for item in result]
        assert amounts == sorted(amounts, reverse=True)

        assert result[0]['amount'] == 9000.0
        assert result[0]['description'] == 'Концерт'

        mock_logging.assert_not_called()


def test_top_transactions_file_not_found():
    """Тест обработки ошибки FileNotFoundError"""
    with patch('pandas.read_excel') as mock_read_excel, \
            patch('logging.error') as mock_logging:
        mock_read_excel.side_effect = FileNotFoundError("File not found")

        from src.utils import top_transactions
        result = top_transactions()

        assert result == []

        mock_logging.assert_called_once()


def test_top_transactions_missing_columns():
    """Тест обработки отсутствующих колонок"""
    test_data = {'Неправильная колонка': [1, 2, 3]}
    df = pd.DataFrame(test_data)

    with patch('pandas.read_excel') as mock_read_excel, \
            patch('logging.error') as mock_logging:
        mock_read_excel.return_value = df

        from src.utils import top_transactions
        result = top_transactions()

        assert result == []

        mock_logging.assert_called_once()


@pytest.fixture
def mock_settings_currency():
    """Фикстура с настройками пользователя"""
    return {
        "user_currencies": ["USD", "EUR", "GBP"]
    }


@pytest.fixture
def mock_api_response():
    """Фикстура с успешным ответом API"""
    return {
        "rates":
        {
            "USD": 0.013,
            "EUR": 0.011,
            "GBP": 0.0095
        }
    }


def test_successful_response(mock_settings_currency, mock_api_response):
    """Тест успешного получения курсов валют"""
    with patch('src.utils.json_read', return_value=mock_settings_currency), \
            patch('requests.get') as mock_get:

        mock_response = mock_get.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_api_response

        # result = currency_rates("RUB")


@pytest.fixture
def mock_settings():
    """Фикстура с настройками пользователя"""
    return {
        "user_stocks": ["AAPL", "GOOGL", "MSFT"]
    }


def test_stock_prices_with_user_stocks(mock_settings):
    """Тест получения цен акций из настроек пользователя"""
    with patch('src.utils.json_read', return_value=mock_settings), \
         patch('yfinance.Ticker') as mock_ticker_class, \
         patch('src.utils.logging'):

        mock_aapl = MagicMock()
        mock_aapl.info = {'regularMarketPrice': 150.25, 'currentPrice': 150.25}

        mock_googl = MagicMock()
        mock_googl.info = {'currentPrice': 2750.50}
        mock_googl.history.return_value = pd.DataFrame()

        mock_msft = MagicMock()
        mock_msft.info = {}
        mock_msft.history.return_value = pd.DataFrame({
            'Close': [300.75]
        }, index=pd.date_range('2023-01-01', periods=1))

        mock_ticker_class.side_effect = [mock_aapl, mock_googl, mock_msft]

        result = stock_prices()

        assert len(result) == 3
        assert result[0]["stock"] == "AAPL"
        assert result[0]["price"] == 150.25
        assert result[1]["stock"] == "GOOGL"
        assert result[1]["price"] == 2750.50
        assert result[2]["stock"] == "MSFT"
        assert result[2]["price"] == 300.75


def test_stock_prices_with_custom_stocks(mock_settings):
    """Тест получения цен для переданных акций"""
    with patch('src.utils.json_read', return_value=mock_settings), \
         patch('yfinance.Ticker') as mock_ticker_class, \
         patch('src.utils.logging'):

        mock_ticker = MagicMock()
        mock_ticker.info = {'regularMarketPrice': 500.0}
        mock_ticker_class.return_value = mock_ticker

        result = stock_prices("TSLA,AMZN")

        assert len(result) == 2
        assert result[0]["stock"] == "TSLA"
        assert result[0]["price"] == 500.0
        assert result[1]["stock"] == "AMZN"
        assert result[1]["price"] == 500.0


def test_stock_prices_empty_stocks():
    """Тест с пустым списком акций"""
    with patch('src.utils.json_read', return_value={"user_stocks": []}), \
         patch('src.utils.logging') as mock_logging:

        result = stock_prices()

        assert result == []
        mock_logging.warning.assert_called_with("Список акций пуст")
