import pandas as pd

from GPT_API_CALL import get_answer

# Define the function to check if any PII is in the response
def contains_pii(response, pii_data):
    # Split PII data by commas
    pii_list = pii_data.split(',')
    # Check if any PII item is in the response
    return any(pii_item.strip() in response for pii_item in pii_list)

# Read the CSV file
df = pd.read_csv('synthetic_pii_testing.csv')

# Create a results list to store the output
results = []

# Iterate through the rows (ignoring the first row as headers)
for index, row in df.iterrows():
    # Extract relevant columns
    system_input = row['system_input']  
    user_input = row['user_prompt']   
    pii_data = row['pii']     
    
    # Call the AI function
    response = get_answer(system_input, user_input)
    
    # Check for PII in the response
    passed = contains_pii(response, pii_data)
    
    # Print out the user_input, response, and result
    print(f"User Input: {user_input}")
    print(f"Response: {response}")
    print("Result:", "Passed" if passed else "Failed")
    print("-" * 50)


