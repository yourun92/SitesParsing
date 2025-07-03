import pandas as pd

# Путь к файлу
excel_file = '23_06_2025\\Все_сайты_по_отдельности.xlsx'

# Считываем все листы в виде словаря: {имя_листа: DataFrame}
sheets = pd.read_excel(excel_file, sheet_name=None)

all_rows = []

for sheet_name, df in sheets.items():
    # Обрабатываем названия колонок: обрезаем по запятой, Capitalized
    df.columns = [
        col.split(',')[0].strip().capitalize() if isinstance(col, str) else col
        for col in df.columns
    ]

    rows = df.dropna(how='all').to_dict(orient='records')
    all_rows.extend(rows)

# Создаем DataFrame из всех строк
df = pd.DataFrame(all_rows)

# Удаляем колонки, в которых заполнено менее 5% значений
min_fill_ratio = 0.05
min_count = len(df) * min_fill_ratio
df = df.dropna(axis=1, thresh=min_count)

df.to_excel('23_06_2025\\Общая_таблица.xlsx', index=False)
