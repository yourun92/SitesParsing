import pandas as pd
import pytesseract


data = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DATAFRAME)
data = data[data.text.notnull()]
print(data[['left', 'top', 'width', 'height', 'text']])