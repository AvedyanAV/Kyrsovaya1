import json
import pandas as pd
from src.services import person_transfers
from src.reports import spending_by_weekday
from src.views import main


if __name__ == "__main__":
    input_date_time = "2025-01-15 14:30:00"
    result_json = main(input_date_time)

    print(json.dumps(result_json, ensure_ascii=False, indent=2))
    print(person_transfers())
    pd = pd.read_excel(r'/Users/avedyanav/PycharmProjects/Kyrsovaya1/data/operations.xlsx')
    print(spending_by_weekday(pd))
