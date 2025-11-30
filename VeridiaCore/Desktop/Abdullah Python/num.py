import pandas as pd
import numpy as np

# Data with Pandas
data = {
    'Name': ['Ali', 'Sara', 'John'],
    'Age': [25, 30, 22],
    'City': ['Lahore', 'Karachi', 'Islamabad']
}
df = pd.DataFrame(data)

# Convert Age to NumPy array
age_array = np.array(df['Age'])

print("🔢 NumPy array of ages:")
print(age_array)

# Calculate mean age using NumPy
mean_age = np.mean(age_array)
print("📏 Mean Age:", mean_age)

# Add a new column 'Age Plus 5' using NumPy
df['Age Plus 5'] = age_array + 5

print("📋 Updated DataFrame:")
print(df)
