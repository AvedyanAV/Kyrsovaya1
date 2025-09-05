import pandas as pd
from typing import Optional
import datetime


def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает средние траты в каждый из дней недели за последние три месяца"""

    if date is None:
        current_date = datetime.datetime.now().date()
    else:
        current_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    start_date = current_date - datetime.timedelta()

    required_columns = ['Дата операции', 'Сумма операции']
    missing_columns = [col for col in required_columns if col not in transactions.columns]

    if missing_columns:
        raise ValueError(f"Отсутствуют необходимые колонки: {missing_columns}")

    transactions_copy = transactions.copy()
    transactions_copy['Дата операции'] = pd.to_datetime(transactions_copy['Дата операции'], errors='coerce')

    mask = (transactions_copy['Дата операции'] >= pd.Timestamp(start_date)) & \
           (transactions_copy['Дата операции'] <= pd.Timestamp(current_date))
    recent_transactions = transactions_copy[mask].copy()

    recent_transactions = recent_transactions[recent_transactions['Сумма операции'] < 0].copy()

    if recent_transactions.empty:
        return pd.DataFrame({
            'day_of_week': ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
            'average_spending': [0.0] * 7
        })

    recent_transactions['day_of_week_num'] = recent_transactions['Дата операции'].dt.dayofweek
    recent_transactions['day_of_week_name'] = recent_transactions['Дата операции'].dt.day_name('ru_RU')

    result = recent_transactions.groupby(['day_of_week_num', 'day_of_week_name'])['Сумма операции'].agg([
        ('average_spending', 'mean'),
        ('transaction_count', 'count')
    ]).reset_index()

    result = result.sort_values('day_of_week_num')

    result['average_spending'] = result['average_spending'].abs().round(2)

    days_map = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }

    full_week = pd.DataFrame({
        'day_of_week_num': range(7),
        'day_of_week_name': list(days_map.values())
    })

    result = full_week.merge(result, on=['day_of_week_num', 'day_of_week_name'], how='left')
    result['average_spending'] = result['average_spending'].fillna(0.0)
    result['transaction_count'] = result['transaction_count'].fillna(0)

    return result[['day_of_week_name', 'average_spending', 'transaction_count']]
