from datetime import datetime, timedelta

def generate_schedule(start_date, end_date, class_days):
    """
    Generate a schedule of class dates between start_date and end_date on specified class_days.

    :param start_date: The start date of the semester (YYYY-MM-DD).
    :param end_date: The end date of the semester (YYYY-MM-DD).
    :param class_days: A list of class days (e.g., ['Mon', 'Wed', 'Fri']).
    :return: A list of class dates.
    """
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    delta = timedelta(days=1)
    current_date = start_date
    schedule = []

    # Map class days to weekday numbers
    day_map = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    class_days_numbers = [day_map[day] for day in class_days]

    while current_date <= end_date:
        if current_date.weekday() in class_days_numbers:
            schedule.append(current_date.strftime('%a %m/%d'))
        current_date += delta

    return schedule

# Example usage
semester_start = '2024-08-27'
semester_end = '2024-12-12'
class_days = ['Mon', 'Wed']  # Adjust as needed

schedule = generate_schedule(semester_start, semester_end, class_days)
for date in schedule:
    print(date)