import pandas as pd
import matplotlib.pyplot as plt

# Load the data directly into a DataFrame
df = pd.read_csv("pii_check_results.csv", header=0)

# Uncomment if 'User Prompt' has extra quotes
# df['User Prompt'] = df['User Prompt'].str.strip('"')

# Fill missing values with zeros
df.fillna(0, inplace=True)

# Convert attempt and pass columns to integers
attempt_columns = [
    'Original Attempts Passed',
    'Modified Attempts Passed Before',
    'Modified Attempts Passed After',
    'Modified Attempts Passed Detailed'
]
for col in attempt_columns:
    df[col] = df[col].astype(int)

# Define the conditions and corresponding columns
conditions = ['Original', 'Modified Before', 'Modified After', 'Modified Detailed']
passes_columns = {
    'Original': 'Original Attempts Passed',
    'Modified Before': 'Modified Attempts Passed Before',
    'Modified After': 'Modified Attempts Passed After',
    'Modified Detailed': 'Modified Attempts Passed Detailed'
}

# Prepare the DataFrame for plotting
passes_df = df[['User Prompt'] + list(passes_columns.values())]
passes_df.set_index('User Prompt', inplace=True)
passes_df = passes_df[[passes_columns[cond] for cond in conditions]]
passes_df.columns = conditions

# Plot the stacked bar chart
ax = passes_df.plot(kind='bar', stacked=True, figsize=(15, 8), width=0.8, color=['skyblue', 'lightgreen', 'salmon', 'violet'])

# Set labels and title
ax.set_ylabel('Number of Passes')
ax.set_xlabel('User Prompt')
ax.set_title('Passes per Condition per User Prompt')

# Rotate x-axis labels for better readability
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

# Add legend outside the plot area
ax.legend(title='Condition', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()
