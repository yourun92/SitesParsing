import pandas as pd

def sort_columns_by_fill(df, fixed_columns=None, num_fixed=7):
    """
    Сортирует колонки по заполненности, оставляя фиксированные колонки на месте

    Параметры:
    df - исходный DataFrame
    fixed_columns - список колонок, которые нужно оставить на своих местах
    num_fixed - сколько колонок оставить фиксированными, если fixed_columns не указан
    """
    # Определяем фиксированные колонки
    if fixed_columns is None:
        fixed_columns = df.columns[:num_fixed]

    # Колонки для сортировки (все кроме фиксированных)
    sortable_columns = [col for col in df.columns if col not in fixed_columns]

    # Считаем количество непустых значений для каждой колонки
    fill_counts = df[sortable_columns].count().sort_values(ascending=False)

    # Новый порядок колонок: сначала фиксированные, затем отсортированные по заполненности
    new_columns_order = list(fixed_columns) + list(fill_counts.index)

    return df[new_columns_order]

# Пример использования
# df = pd.read_excel('ваш_файл.xlsx')
# fixed_cols = ['ID', 'Name', 'Date']  # или оставить None для первых 7 колонок
# sorted_df = sort_columns_by_fill(df, fixed_columns=fixed_cols)