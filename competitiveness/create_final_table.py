import pandas as pd
import numpy as np

# Load both datasets
print("Loading house election data...")
house_df = pd.read_csv('1976-2024-house.tab')  # It's actually comma-separated
bias_df = pd.read_csv('bias_ushouse.csv')

print(f"House data shape: {house_df.shape}")
print(f"Bias data shape: {bias_df.shape}")

# Convert numeric columns
house_df['year'] = pd.to_numeric(house_df['year'])
house_df['district'] = pd.to_numeric(house_df['district'])
house_df['candidatevotes'] = pd.to_numeric(house_df['candidatevotes'])
house_df['totalvotes'] = pd.to_numeric(house_df['totalvotes'])

# Filter for general elections only and major parties
print("Filtering for general elections and major parties...")
house_df = house_df[house_df['stage'] == 'GEN']
house_df = house_df[house_df['party'].isin(['DEMOCRAT', 'REPUBLICAN'])]

print(f"After filtering: {house_df.shape}")

# Group by year, state, and district to get Democratic and Republican votes
print("Aggregating votes by district...")
district_votes = house_df.groupby(['year', 'state', 'district', 'party'])['candidatevotes'].sum().unstack(fill_value=0)

# Calculate total votes and percentages
district_votes['total_votes'] = district_votes['DEMOCRAT'] + district_votes['REPUBLICAN']
district_votes['democratic_vote_percentage'] = (district_votes['DEMOCRAT'] / district_votes['total_votes']) * 100
district_votes['republican_vote_percentage'] = (district_votes['REPUBLICAN'] / district_votes['total_votes']) * 100

# Reset index to make columns accessible
district_votes = district_votes.reset_index()

print(f"Aggregated data shape: {district_votes.shape}")
print("Sample of aggregated data:")
print(district_votes[['year', 'state', 'district', 'democratic_vote_percentage', 'republican_vote_percentage']].head(10))

# Now try to merge with bias data
print("\nAttempting to merge with bias data...")

# Create state abbreviation mapping
state_abbr = {
    'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR', 'CALIFORNIA': 'CA',
    'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE', 'FLORIDA': 'FL', 'GEORGIA': 'GA',
    'HAWAII': 'HI', 'IDAHO': 'ID', 'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA',
    'KANSAS': 'KS', 'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS', 'MISSOURI': 'MO',
    'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV', 'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ',
    'NEW MEXICO': 'NM', 'NEW YORK': 'NY', 'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH',
    'OKLAHOMA': 'OK', 'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT', 'VERMONT': 'VT',
    'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 'WYOMING': 'WY'
}

# Add state abbreviation to house data
district_votes['state_abbr'] = district_votes['state'].map(state_abbr)

# Create merge keys
district_votes['merge_key'] = district_votes['state_abbr'] + district_votes['year'].astype(str)
bias_df['merge_key'] = bias_df['state'] + bias_df['year'].astype(str)

print(f"\nUnique state-year combinations in house data: {len(district_votes['merge_key'].unique())}")
print(f"Unique state-year combinations in bias data: {len(bias_df['merge_key'].unique())}")

# Find overlapping years
house_years = sorted(district_votes['year'].unique())
bias_years = sorted(bias_df['year'].unique())
common_years = sorted(set(house_years) & set(bias_years))

print(f"House data years: {house_years[:5]}...{house_years[-5:]}")
print(f"Bias data years: {bias_years[:5]}...{bias_years[-5:]}")
print(f"Common years: {common_years[:10]}...{common_years[-10:]}")

# Merge the datasets
merged_data = pd.merge(district_votes, bias_df[['merge_key', 'eg_adj_avg', 'bias_avg']],
                      on='merge_key', how='inner')

print(f"\nMerged data shape: {merged_data.shape}")
print("Sample of merged data:")
print(merged_data[['year', 'state', 'district', 'democratic_vote_percentage',
                   'republican_vote_percentage', 'eg_adj_avg', 'bias_avg']].head(10))

# Create final table
final_table = merged_data[[
    'year',
    'state',
    'district',
    'democratic_vote_percentage',
    'republican_vote_percentage',
    'eg_adj_avg',  # efficiency gap
    'bias_avg'     # bias
]].copy()

# Create district name
final_table['district_name'] = final_table['state'] + ' - District ' + final_table['district'].astype(str) + ' (' + final_table['year'].astype(str) + ')'

# Rename columns for clarity
final_table = final_table.rename(columns={
    'eg_adj_avg': 'efficiency_gap',
    'bias_avg': 'bias'
})

# Reorder and round
final_table = final_table[[
    'district_name',
    'democratic_vote_percentage',
    'republican_vote_percentage',
    'efficiency_gap',
    'bias'
]]

# Round values
final_table['democratic_vote_percentage'] = final_table['democratic_vote_percentage'].round(2)
final_table['republican_vote_percentage'] = final_table['republican_vote_percentage'].round(2)
final_table['efficiency_gap'] = final_table['efficiency_gap'].round(4)
final_table['bias'] = final_table['bias'].round(4)

print(f"\nFinal table shape: {final_table.shape}")
print("Sample of final table:")
print(final_table.head(15))

# Save the final table
final_table.to_csv('election_district_final_table.csv', index=False)
print(f"\nFinal table saved to 'election_district_final_table.csv'")

# Show statistics
print(f"\nFinal table statistics:")
print(final_table[['democratic_vote_percentage', 'republican_vote_percentage',
                   'efficiency_gap', 'bias']].describe())

# Show examples by decade
print(f"\nExamples from 1980s:")
print(final_table[final_table['district_name'].str.contains('198')].head(5))

print(f"\nExamples from 2000s:")
print(final_table[final_table['district_name'].str.contains('200')].head(5))