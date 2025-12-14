import pandas as pd

# Step 1: Create the data
data = {
    'Name': ['Ali', 'Sara', 'John'],
    'Age': [25, 30, 22],
    'City': ['Lahore', 'Karachi', 'Islamabad']
}

# Step 2: Create DataFrame
df = pd.DataFrame(data)

# Step 3: Print full DataFrame
print("📋 Full DataFrame:")
print(df)
print("-" * 40)

# Step 4: Show only first 2 rows
print("👀 First 2 rows:")
print(df.head(2))
print("-" * 40)

# Step 5: Show DataFrame shape (rows, columns)
print("📐 Shape of DataFrame:")
print(df.shape)
print("-" * 40)

# Step 6: Describe numeric data (summary stats)
print("📊 Summary Statistics:")
print(df.describe())
print("-" * 40)

# Step 7: Access a single column (Names)
print("📝 Names Column:")
print(df['Name'])
print("-" * 40)

# Step 8: Access row by index (row 1 ➔ Sara)
print("🔍 Row by Index:")
print(df.iloc[1])   # index starts from 0
print("-" * 40)

# Step 9: Filter rows (Age > 23)
print("🔎 People older than 23:")
print(df[df['Age'] > 23])
print("-" * 40)

# Step 10: Add a new column (Country)
df['Country'] = 'Pakistan'
print("🌍 DataFrame after adding Country column:")
print(df)
print("-" * 40)

# Step 11: Save to CSV
df.to_csv('my_output.csv', index=False)
print("✅ Data saved to my_output.csv")
