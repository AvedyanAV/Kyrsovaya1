import datetime
import logging
from src.utils import greeting, currency_rates, stock_prices, cards, top_transactions


def main(input_datetime: str) -> dict:
    """Главная функция, принимающая строку с датой и временем и возвращающая JSON-ответ"""

    response = {
        "greeting": "",
        "cards": [],
        "top_transactions": [],
        "currency_rates": [],
        "stock_prices": []
    }

    try:
        input_dt = datetime.datetime.strptime(input_datetime, "%Y-%m-%d %H:%M:%S")

        response["greeting"] = greeting()

        cards_data = cards()
        if cards_data:
            response["cards"] = list(cards_data.values())

        top_trans = top_transactions()
        response["top_transactions"] = top_trans

        currency_data = currency_rates()
        if currency_data:
            response["currency_rates"] = currency_data

        stocks_data = stock_prices()
        if stocks_data:
            response["stock_prices"] = stocks_data

    except ValueError:
        logging.error("Неверный формат входной даты. Ожидается YYYY-MM-DD HH:MM:SS")
        response["error"] = "Неверный формат входной даты"
    except Exception as e:
        logging.error(f"Неожиданная ошибка в главной функции: {e}")
        response["error"] = f"Внутренняя ошибка: {str(e)}"

    return response
