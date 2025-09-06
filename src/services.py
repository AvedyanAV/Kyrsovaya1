import re
import logging
import pandas as pd


def person_transfers() -> list:
    """Функция возвращает JSON со всеми транзакциями-переводами физлицам"""
    file_path = r'/Users/avedyanav/PycharmProjects/Kyrsovaya1/data/operations.xlsx'

    try:
        df = pd.read_excel(file_path)

        required_columns = ['Категория', 'Описание', 'Сумма операции', 'Дата операции']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logging.error(f"В файле отсутствуют необходимые колонки: {missing_columns}")
            return []

        transfers_mask = (df['Категория'] == 'Переводы') & df['Описание'].str.contains(r'[А-Яа-я]+\s[А-Я]\.', na=False)

        person_transfers_df = df[transfers_mask]

        result = []
        for _, row in person_transfers_df.iterrows():
            try:
                description = str(row['Описание']).strip()
                name_match = re.search(r'^([А-Яа-я]+)\s[А-Я]\.', description)
                recipient = name_match.group(1) if name_match else description

                result.append({
                    "recipient": recipient,
                    "description": description,
                    "amount": float(row['Сумма операции']),
                    "date": str(row['Дата операции']).strip() if pd.notna(row['Дата операции']) else "Не указана"
                })

            except (ValueError, TypeError) as e:
                logging.warning(f"Ошибка обработки строки перевода: {row}. Ошибка: {e}")
                continue

        return result

    except FileNotFoundError:
        logging.error(f"Файл {file_path} не найден")
        return []
