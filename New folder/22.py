import pandas as pd
import math
import os

def split_excel(input_file, rows_per_file=10, output_folder="chunks"):
    df = pd.read_excel(input_file, engine="openpyxl")
    total_rows = len(df)
    num_chunks = math.ceil(total_rows / rows_per_file)
    os.makedirs(output_folder, exist_ok=True)

    for i in range(num_chunks):
        start = i * rows_per_file
        end = start + rows_per_file
        chunk = df.iloc[start:end]
        filename = os.path.join(output_folder, f"chunk_{i+1:03}.xlsx")
        chunk.to_excel(filename, index=False, engine="openpyxl")
        print(f"✅ Created {filename} ({len(chunk)} rows)")

    print(f"\n🎯 Total: {num_chunks} files in '{output_folder}'")

if __name__ == "__main__":
    split_excel("your_file.xlsx", rows_per_file=10, output_folder="chunks")
