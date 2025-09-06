from unittest.mock import patch
from src.views import main


def test_main_invalid_datetime_format():
    """Тест обработки неверного формата даты"""
    result = main("invalid-date-format")

    assert "error" in result
    assert "Неверный формат входной даты" in result["error"]
    assert result["greeting"] == ""
    assert result["cards"] == []
    assert result["top_transactions"] == []
    assert result["currency_rates"] == []
    assert result["stock_prices"] == []


def test_main_valid_datetime():
    """Тест корректной работы функции с валидной датой"""
    with patch('src.views.greeting') as mock_greeting, \
            patch('src.views.cards') as mock_cards, \
            patch('src.views.top_transactions') as mock_top_trans, \
            patch('src.views.currency_rates') as mock_currency, \
            patch('src.views.stock_prices') as mock_stocks:
        mock_greeting.return_value = "Добро пожаловать!"
        mock_cards.return_value = {"card1": {"id": 1, "balance": 1000}}
        mock_top_trans.return_value = [{"amount": 500, "description": "Покупка"}]
        mock_currency.return_value = [{"currency": "USD", "rate": 75.5}]
        mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]

        result = main("2024-01-15 12:30:45")

        assert result["greeting"] == "Добро пожаловать!"
        assert result["cards"] == [{"id": 1, "balance": 1000}]
        assert result["top_transactions"] == [{"amount": 500, "description": "Покупка"}]
        assert result["currency_rates"] == [{"currency": "USD", "rate": 75.5}]
        assert result["stock_prices"] == [{"stock": "AAPL", "price": 150.0}]
        assert "error" not in result

        mock_greeting.assert_called_once()
        mock_cards.assert_called_once()
        mock_top_trans.assert_called_once()
        mock_currency.assert_called_once()
        mock_stocks.assert_called_once()
