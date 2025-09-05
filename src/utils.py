import json
import requests
import datetime
import logging
import pandas as pd
import yfinance as yf


def json_read() -> dict:
    """Функция считывает json файл для настройки поиска валют и акции"""

    file_path = r'/Users/avedyanav/PycharmProjects/Kyrsovaya1/data/user_settings.json'

    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        logging.error("Файл data/user_settings.json не найден")
        return {}
    except json.JSONDecodeError:
        logging.error("Ошибка при чтении JSON файла")
        return {}


def greeting() -> str:
    """Функция приветствует пользователя в зависимости от времени суток"""

    time_now = datetime.datetime.now().hour

    if 6 <= time_now < 10:
        return "Доброе утро"
    elif 10 <= time_now < 18:
        return "Добрый день"
    elif 18 <= time_now < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def cards() -> dict:
    """Функция обрабатывает данные по банковским картам"""
    file_path = r'/Users/avedyanav/PycharmProjects/Kyrsovaya1/data/operations.xlsx'
    cards_data = {}

    try:
        df = pd.read_excel(file_path)

        if 'Номер карты' not in df.columns or 'Сумма операции' not in df.columns:
            logging.error("В файле отсутствуют необходимые колонки: 'Номер карты' и 'Сумма операции'")
            return {}

        for _, row in df.iterrows():
            try:
                card_number = str(row['Номер карты']).strip()
                amount = float(row['Сумма операции'])

                if len(card_number) >= 4:
                    last_digits = card_number[-4:]

                if last_digits not in cards_data:
                    cards_data[last_digits] = {
                        'last_digits': last_digits,
                        'total_spent': 0.0,
                        'cashback': 0.0
                    }

                if amount < 0:
                    cards_data[last_digits]['total_spent'] += abs(amount)

                    cashback_earned = abs(amount) // 100
                    cards_data[last_digits]['cashback'] += cashback_earned

            except (ValueError, TypeError) as e:
                logging.warning(f"Ошибка обработки строки: {row}. Ошибка: {e}")
                continue

        for card_data in cards_data.values():
            card_data['total_spent'] = round(card_data['total_spent'], 2)
            card_data['cashback'] = round(card_data['cashback'], 2)

        return cards_data

    except FileNotFoundError:
        logging.error(f"Файл {file_path} не найден")
        return {}
    except Exception as e:
        logging.error(f"Ошибка при чтении файла: {e}")
        return {}


def top_transactions():
    """Функция показывает топ-5 транзакций по сумме платежа"""
    file_path = r'/Users/avedyanav/PycharmProjects/Kyrsovaya1/data/operations.xlsx'

    try:
        df = pd.read_excel(file_path)

        required_columns = ['Дата платежа', 'Сумма операции с округлением', 'Категория', 'Описание']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logging.error(f"В файле отсутствуют необходимые колонки: {missing_columns}")
            return []

        df['Сумма операции с округлением'] = pd.to_numeric(df['Сумма операции с округлением'], errors='coerce')
        df = df.dropna(subset=['Сумма операции с округлением'])

        top_5 = df.nlargest(5, 'Сумма операции с округлением')

        result = []
        for _, row in top_5.iterrows():
            result.append({
                'date': str(row['Дата платежа']).strip(),
                'amount': float(row['Сумма операции с округлением']),
                'category': str(row['Категория']).strip(),
                'description': str(row['Описание']).strip()
            })

        return result

    except FileNotFoundError:
        logging.error(f"Файл не найден: {file_path}")
        return []
    except Exception as e:
        logging.error(f"Ошибка при чтении файла: {e}")
        return []


def currency_rates(base_currency: str = "RUB") -> list:
    """Функция получает курсы валют из настроек относительно базовой валюты"""
    try:
        settings = json_read()
        user_currencies = settings.get("user_currencies", [])

        if not user_currencies:
            logging.error("Список валют пользователя пуст")
            return []

        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        result = []
        for currency in user_currencies:
            rate = data['rates'].get(currency)
            if rate is not None:
                converted_rate = round(1 / rate, 2)
                result.append({
                    "currency": currency,
                    "rate": converted_rate
                })
            else:
                logging.warning(f"Валюта {currency} не найдена в ответе API")
                result.append({
                    "currency": currency,
                    "rate": None
                })

        return result

    except requests.RequestException as e:
        logging.error(f"Ошибка запроса: {e}")
        return []
    except (KeyError, ValueError) as e:
        logging.error(f"Ошибка обработки данных: {e}")
        return []


def stock_prices(stocks: str = None) -> list:
    """Функция показывает стоимость акций из S&P500"""
    settings = json_read()
    user_stocks = settings.get("user_stocks", [])

    if isinstance(stocks, str):
        stocks_to_check = [stock.strip() for stock in stocks.split(',') if stock.strip()]
    else:
        stocks_to_check = user_stocks

    results = []

    if not stocks_to_check:
        logging.warning("Список акций пуст")
        return []

    try:
        for stock in stocks_to_check:
            try:
                ticker = yf.Ticker(stock)
                info = ticker.info

                price = (info.get('regularMarketPrice') or
                         info.get('currentPrice') or
                         info.get('regularMarketPreviousClose'))

                if price is None:
                    hist = ticker.history(period="1d")
                    if not hist.empty and len(hist) > 0:
                        price = hist['Close'].iloc[-1]

                if price is not None:
                    results.append({
                        "stock": stock,
                        "price": round(float(price), 2)
                    })
                else:
                    results.append({
                        "stock": stock,
                        "price": None
                    })
                    logging.warning(f"Акция {stock} не найдена или цена недоступна")

            except Exception as e:
                results.append({
                    "stock": stock,
                    "price": None
                })
                logging.error(f"Ошибка получения цены для {stock}: {e}")

        return results

    except Exception as e:
        logging.error(f"Неожиданная ошибка: {e}")
        return []
