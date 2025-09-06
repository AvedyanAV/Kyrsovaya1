import pandas as pd
from typing import Optional
import datetime


def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция возвращает средние траты в каждый из дней недели
    за последние три месяца от указанной даты.
    """

    df = transactions.copy()

    required_columns = ['Дата платежа', 'Сумма операции с округлением']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Отсутствуют необходимые колонки: {missing_columns}")

    df['Дата платежа'] = pd.to_datetime(
        df['Дата платежа'],
        format='%d.%m.%Y',
        dayfirst=True,
        errors='coerce'
    )

    df = df.dropna(subset=['Дата платежа'])

    if len(df) == 0:
        weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг',
                    'Пятница', 'Суббота', 'Воскресенье']
        return pd.DataFrame({
            'День недели': weekdays,
            'Средние траты': [0] * 7
        })

    if date is None:
        end_date = df['Дата платежа'].max().date()
    else:
        end_date = datetime.datetime.strptime(date, "%d.%m.%Y").date()
        max_data_date = df['Дата платежа'].max().date()
        if end_date > max_data_date:
            end_date = max_data_date
            print(f"Предупреждение: переданная дата позже последней даты в данных. Используется {end_date}")

    start_date = end_date - datetime.timedelta(days=90)

    mask = (df['Дата платежа'].dt.date >= start_date) & (df['Дата платежа'].dt.date <= end_date)
    df_filtered = df.loc[mask].copy()

    if len(df_filtered) == 0:
        print("Нет данных за указанный период. Используем все доступные данные.")
        df_filtered = df.copy()

    df_filtered['День недели'] = df_filtered['Дата платежа'].dt.dayofweek

    result = (df_filtered.groupby('День недели')['Сумма операции с округлением']
              .mean()
              .reset_index()
              .rename(columns={'Сумма операции с округлением': 'Средние траты'}))

    result['Средние траты'] = result['Средние траты'].round().astype(int)

    weekdays_map = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }

    result['День недели'] = result['День недели'].map(weekdays_map)

    all_weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг',
                    'Пятница', 'Суббота', 'Воскресенье']

    for weekday in all_weekdays:
        if weekday not in result['День недели'].values:
            result = pd.concat([result, pd.DataFrame({
                'День недели': [weekday],
                'Средние траты': [0]
            })], ignore_index=True)

    result['День недели'] = pd.Categorical(result['День недели'], categories=all_weekdays, ordered=True)
    result = result.sort_values('День недели').reset_index(drop=True)

    return result
