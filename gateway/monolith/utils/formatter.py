from datetime import datetime


def my_date_formatter(text):
    date_dt2 = datetime.strptime(text, "%Y-%m-%d %H:%M:%S.%f")
    return date_dt2.strftime("%d/%m/%Y %H:%M:%S")

def my_date_formatter_iso(text):
    date_dt2 = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    return date_dt2.strftime("%d/%m/%Y %H:%M:%S")