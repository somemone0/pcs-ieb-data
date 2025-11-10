import pandas as pd
import numpy as np

# Load the final table
df = pd.read_csv('election_district_final_table.csv')

print(f"Original data shape: {df.shape}")
print("Original data sample:")
print(df.head())

# Debug the splitting process
print("Testing split on sample data:")
sample_name = df['district_name'].iloc[0]
print(f"Sample: {sample_name}")
test_split = sample_name.split(' - ')
print(f"Split result: {test_split}")
print(f"Split length: {len(test_split)}")

# Split district_name into separate columns
# Format: "STATE - District X (YEAR)"
split_data = df['district_name'].str.split(' - ', expand=True)

print(f"Split data shape: {split_data.shape}")
print("Split data columns:")
for i in range(min(5, split_data.shape[1])):
    print(f"Column {i}: {split_data[i].iloc[:3].tolist()}")

if split_data.shape[1] >= 2:
    df['state'] = split_data[0]
    df['rest'] = split_data[1]

    # Extract district number and year using regex pattern
    # Format: "District X (YEAR)"
    import re

    # Extract district number
    df['district_number'] = df['rest'].str.extract(r'District (\d+)').astype(int)

    # Extract year
    df['year'] = df['rest'].str.extract(r'\((\d{4})\)').astype(int)

    # Clean up temporary columns
    df = df.drop(['district_name', 'rest'], axis=1)
else:
    print("Error: District name format is not as expected")
    print("Sample district names:")
    print(df['district_name'].head())
    exit()

# Reorder columns to put state, district_number, and year first
final_columns = ['state', 'district_number', 'year', 'democratic_vote_percentage',
                'republican_vote_percentage', 'efficiency_gap', 'bias']

df = df[final_columns]

print(f"\nAfter splitting columns:")
print(f"Data shape: {df.shape}")
print("Sample data:")
print(df.head(15))

# Verify the parsing worked correctly
print(f"\nData types:")
print(df.dtypes)

# Check for any parsing issues
print(f"\nChecking for any parsing issues:")
print(f"Unique states: {df['state'].nunique()}")
print(f"State sample: {sorted(df['state'].unique())[:10]}")
print(f"District number range: {df['district_number'].min()} to {df['district_number'].max()}")
print(f"Year range: {df['year'].min()} to {df['year'].max()}")

# Save the updated table
df.to_csv('election_district_table_split.csv', index=False)
print(f"\nUpdated table saved to 'election_district_table_split.csv'")

# Show some examples
print(f"\nExamples by state:")
for state in ['ALABAMA', 'CALIFORNIA', 'TEXAS', 'NEW YORK']:
    if state in df['state'].values:
        print(f"\n{state} examples:")
        print(df[df['state'] == state][['state', 'district_number', 'year',
                                       'democratic_vote_percentage']].head(3))

# Summary statistics by state
print(f"\nSummary by state (top 10 states by number of districts):")
state_counts = df['state'].value_counts().head(10)
print(state_counts)