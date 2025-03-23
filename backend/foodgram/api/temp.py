import locale

from datetime import datetime

locale.setlocale(
    category=locale.LC_ALL,
    locale='ru_RU.UTF-8'
)

date = datetime.now().strftime('%Y-%b-%d')
print(date)