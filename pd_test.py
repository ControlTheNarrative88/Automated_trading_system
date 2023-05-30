import pandas as pd


# Your existing DataFrame
df = pd.DataFrame({
    'Current Trend': [False, True, False, True, False],
}, index=pd.to_datetime(['2020-10-28', '2020-11-05', '2021-01-29', '2021-02-08', '2021-03-04']))

# Create a new DataFrame with a daily frequency
new_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
new_df = pd.DataFrame(index=new_index)

# Merge the new DataFrame with the existing one
merged_df = pd.merge(new_df, df, how='left', left_index=True, right_index=True)

# Forward-fill the missing values
filled_df = merged_df.ffill()

# Display the filled DataFrame
print(filled_df)



