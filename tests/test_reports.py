import pytest
import pandas as pd
from src.reports import spending_by_weekday


def test_missing_required_columns():
    """Тест на отсутствие обязательных колонок"""
    df = pd.DataFrame({'Дата': ['01.01.2023'], 'Сумма': [100]})

    with pytest.raises(ValueError, match="Отсутствуют необходимые колонки:"):
        spending_by_weekday(df)


def test_empty_dataframe():
    """Тест с пустым DataFrame"""
    df = pd.DataFrame(columns=['Дата платежа', 'Сумма операции с округлением'])

    result = spending_by_weekday(df)

    assert len(result) == 7
    assert all(result['Средние траты'] == 0)
    assert list(result['День недели']) == [
        'Понедельник', 'Вторник', 'Среда', 'Четверг',
        'Пятница', 'Суббота', 'Воскресенье'
    ]


def test_basic_functionality():
    """Тест базовой функциональности"""
    test_dates = [
        '02.01.2023',
        '03.01.2023',
        '04.01.2023',
    ]

    df = pd.DataFrame({
        'Дата платежа': test_dates * 2,
        'Сумма операции с округлением': [100, 200, 300] * 2
    })

    result = spending_by_weekday(df, date='05.01.2023')

    assert len(result) == 7
    assert result.loc[result['День недели'] == 'Понедельник', 'Средние траты'].values[0] == 100
    assert result.loc[result['День недели'] == 'Вторник', 'Средние траты'].values[0] == 200
    assert result.loc[result['День недели'] == 'Среда', 'Средние траты'].values[0] == 300
