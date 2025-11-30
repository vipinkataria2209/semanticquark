"""Date parser for relative date ranges like 'last week', 'today', etc."""

from datetime import datetime, timedelta, timezone as tz
from typing import List, Optional, Union
import re


def parse_relative_date(date_string: str, timezone: Optional[str] = None) -> List[str]:
    """Parse relative date string to absolute date range.
    
    Supports formats like:
    - today, yesterday, tomorrow
    - last week, last month, last year, last quarter
    - last 7 days, last 30 days, last 6 months
    - next week, next month
    - this week, this month, this year
    - from 7 days ago to now
    - from now to 2 weeks from now
    
    Args:
        date_string: Relative date string
        timezone: Timezone (currently not used, defaults to UTC)
        
    Returns:
        List of two date strings [start, end] in YYYY-MM-DD format
    """
    date_string = date_string.lower().strip()
    now = datetime.now(tz.utc).replace(tzinfo=None)  # Use timezone-aware, then remove tzinfo for compatibility
    
    # today
    if date_string == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
    
    # yesterday
    if date_string == "yesterday":
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        return [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
    
    # tomorrow
    if date_string == "tomorrow":
        tomorrow = now + timedelta(days=1)
        start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        return [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
    
    # this week, last week, next week
    week_match = re.match(r"(this|last|next)\s+week", date_string)
    if week_match:
        direction = week_match.group(1)
        today = now.date()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        
        if direction == "this":
            start = datetime.combine(monday, datetime.min.time())
            end = datetime.combine(sunday, datetime.max.time())
        elif direction == "last":
            start = datetime.combine(monday - timedelta(days=7), datetime.min.time())
            end = datetime.combine(sunday - timedelta(days=7), datetime.max.time())
        else:  # next
            start = datetime.combine(monday + timedelta(days=7), datetime.min.time())
            end = datetime.combine(sunday + timedelta(days=7), datetime.max.time())
        
        return [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
    
    # this month, last month, next month
    month_match = re.match(r"(this|last|next)\s+month", date_string)
    if month_match:
        direction = month_match.group(1)
        if direction == "this":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Last day of current month
            if now.month == 12:
                end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
            end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif direction == "last":
            if now.month == 1:
                start = now.replace(year=now.year - 1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(day=1) - timedelta(days=1)
            else:
                start = now.replace(month=now.month - 1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(day=1) - timedelta(days=1)
            end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:  # next
            if now.month == 12:
                start = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(year=now.year + 1, month=2, day=1) - timedelta(days=1)
            else:
                start = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(month=now.month + 2, day=1) - timedelta(days=1)
            end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
    
    # this year, last year, next year
    year_match = re.match(r"(this|last|next)\s+year", date_string)
    if year_match:
        direction = year_match.group(1)
        if direction == "this":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        elif direction == "last":
            start = now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(year=now.year - 1, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:  # next
            start = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(year=now.year + 1, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        
        return [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
    
    # this quarter, last quarter, next quarter
    quarter_match = re.match(r"(this|last|next)\s+quarter", date_string)
    if quarter_match:
        direction = quarter_match.group(1)
        current_quarter = (now.month - 1) // 3 + 1
        quarter_start_month = (current_quarter - 1) * 3 + 1
        
        if direction == "this":
            start = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            quarter_end_month = quarter_start_month + 2
            if quarter_end_month == 12:
                end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
            else:
                end = now.replace(month=quarter_end_month + 1, day=1) - timedelta(days=1)
                end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif direction == "last":
            if current_quarter == 1:
                start = now.replace(year=now.year - 1, month=10, day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(year=now.year - 1, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
            else:
                prev_quarter = current_quarter - 1
                prev_quarter_start_month = (prev_quarter - 1) * 3 + 1
                start = now.replace(month=prev_quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
                prev_quarter_end_month = prev_quarter_start_month + 2
                end = now.replace(month=prev_quarter_end_month + 1, day=1) - timedelta(days=1)
                end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:  # next
            if current_quarter == 4:
                start = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(year=now.year + 1, month=3, day=31, hour=23, minute=59, second=59, microsecond=999999)
            else:
                next_quarter = current_quarter + 1
                next_quarter_start_month = (next_quarter - 1) * 3 + 1
                start = now.replace(month=next_quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
                next_quarter_end_month = next_quarter_start_month + 2
                end = now.replace(month=next_quarter_end_month + 1, day=1) - timedelta(days=1)
                end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
    
    # last N days, last N weeks, last N months, last N years
    last_n_match = re.match(r"last\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)", date_string)
    if last_n_match:
        n = int(last_n_match.group(1))
        unit = last_n_match.group(2).rstrip('s')
        
        if unit == "day":
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            start = (now - timedelta(days=n)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif unit == "week":
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            start = (now - timedelta(weeks=n)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif unit == "month":
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            # Approximate months as 30 days
            start = (now - timedelta(days=n * 30)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif unit == "year":
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            start = (now - timedelta(days=n * 365)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            raise ValueError(f"Unsupported unit: {unit}")
        
        return [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
    
    # next N days, next N weeks, etc.
    next_n_match = re.match(r"next\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)", date_string)
    if next_n_match:
        n = int(next_n_match.group(1))
        unit = next_n_match.group(2).rstrip('s')
        
        if unit == "day":
            start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = (now + timedelta(days=n)).replace(hour=23, minute=59, second=59, microsecond=999999)
        elif unit == "week":
            start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = (now + timedelta(weeks=n)).replace(hour=23, minute=59, second=59, microsecond=999999)
        elif unit == "month":
            start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = (now + timedelta(days=n * 30)).replace(hour=23, minute=59, second=59, microsecond=999999)
        elif unit == "year":
            start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = (now + timedelta(days=n * 365)).replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            raise ValueError(f"Unsupported unit: {unit}")
        
        return [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
    
    # from X to Y format
    from_to_match = re.match(r"from\s+(.+?)\s+to\s+(.+?)$", date_string)
    if from_to_match:
        from_str = from_to_match.group(1).strip()
        to_str = from_to_match.group(2).strip()
        
        # Parse "X days ago" or "now"
        if from_str == "now":
            start = now
        elif "days ago" in from_str or "day ago" in from_str:
            days_match = re.search(r"(\d+)\s+days?\s+ago", from_str)
            if days_match:
                days = int(days_match.group(1))
                start = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                raise ValueError(f"Cannot parse 'from' date: {from_str}")
        else:
            # Try to parse as absolute date
            try:
                start = datetime.strptime(from_str, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Cannot parse 'from' date: {from_str}")
        
        if to_str == "now":
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif "weeks from now" in to_str or "week from now" in to_str:
            weeks_match = re.search(r"(\d+)\s+weeks?\s+from\s+now", to_str)
            if weeks_match:
                weeks = int(weeks_match.group(1))
                end = (now + timedelta(weeks=weeks)).replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                raise ValueError(f"Cannot parse 'to' date: {to_str}")
        elif "days from now" in to_str or "day from now" in to_str:
            days_match = re.search(r"(\d+)\s+days?\s+from\s+now", to_str)
            if days_match:
                days = int(days_match.group(1))
                end = (now + timedelta(days=days)).replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                raise ValueError(f"Cannot parse 'to' date: {to_str}")
        else:
            # Try to parse as absolute date
            try:
                end = datetime.strptime(to_str, "%Y-%m-%d")
                end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                raise ValueError(f"Cannot parse 'to' date: {to_str}")
        
        return [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]
    
    # If it's already an absolute date, return as-is
    try:
        parsed_date = datetime.strptime(date_string, "%Y-%m-%d")
        return [date_string, date_string]
    except ValueError:
        pass
    
    # If it's a date range array, return as-is
    if isinstance(date_string, list):
        return date_string
    
    raise ValueError(f"Cannot parse relative date: {date_string}")

