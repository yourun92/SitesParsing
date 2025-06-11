import pandas as pd

# Загрузка Excel-файла
df = pd.read_excel("fedast.xlsx")

# Общая длина (кол-во строк)
total_rows = len(df)

# Проход по столбцам и удаление тех, где менее 5% непустых значений
threshold = 0.05  # 5%
columns_to_keep = [col for col in df.columns if df[col].count() / total_rows >= threshold]

# Фильтрация DataFrame
filtered_df = df[columns_to_keep]

filtered_df.drop(columns=['price'], inplace=True)

# Сохранение нового Excel-файла
filtered_df.to_excel("fedast_filtered.xlsx", index=False)

print(f"Удалено {len(df.columns) - len(filtered_df.columns)} столбцов. Осталось {len(filtered_df.columns)}.")