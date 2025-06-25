import calendar
import datetime
from typing import List, Tuple


def add_months(d: datetime.date, months: int) -> datetime.date:

    total_month = d.month - 1 + months
    new_year = d.year + total_month // 12
    new_month = total_month % 12 + 1
    new_day = min(d.day, calendar.monthrange(new_year, new_month)[1])
    return datetime.date(new_year, new_month, new_day)


def get_date_batches(
        start: str,
        end: str,
        batch_months: int = 2,
        min_batches: int = 2
) -> List[Tuple[str, str]]:

    start_date = datetime.datetime.strptime(start, "%Y%m%d").date()
    end_date = datetime.datetime.strptime(end, "%Y%m%d").date()

    total_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
    num_batches = (total_months + batch_months - 1) // batch_months

    if num_batches < min_batches:
        return [
            (
                start_date.strftime("%Y%m%d"),
                end_date.strftime("%Y%m%d")
            )
        ]

    batches: List[Tuple[str, str]] = []
    current_start = start_date
    while current_start <= end_date:
        next_start = add_months(current_start.replace(day=1), batch_months)
        batch_end = min(end_date, next_start - datetime.timedelta(days=1))
        batches.append(
            (
                current_start.strftime("%Y%m%d"),
                batch_end.strftime("%Y%m%d")
            )
        )
        current_start = batch_end + datetime.timedelta(days=1)

    return batches
