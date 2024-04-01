import pandas as pd
import os
import yaml

def prepare_data(params):
    # Load parameters from params.yaml
    locs_id = params['download']['locs_id']
    # Read the CSV file produced by download.py
    csv_file_path = os.path.join('data', f"{locs_id}.csv")
    df = pd.read_csv(csv_file_path)
    # Select columns with names 'DATE' and starting with 'Monthly'
    selected_columns = ['DATE'] + [col for col in df.columns if col.startswith('Monthly')]
    df = df[selected_columns]
    # Check if any 'Monthly' columns have non-empty values
    monthly_columns_with_data = [col for col in df.columns if col != 'DATE' and not df[col].isnull().all()]
    if not monthly_columns_with_data:
        print("No columns have monthly ground truth value.")
    else:
        # Select only the columns with non-empty 'Monthly' values
        df = df[['DATE'] + monthly_columns_with_data]
        # Filter out rows where all 'Monthly' columns are empty
        df = df.dropna(subset=monthly_columns_with_data, how='all')
        # Remove 'Monthly' prefix from column names
        monthly_columns_with_data = [col.replace('Monthly', '') for col in monthly_columns_with_data]
        # Convert DATE column to datetime
        df['DATE'] = pd.to_datetime(df['DATE'])
        # Extract month from the DATE column and create a new column 'Month'
        df['Month'] = df['DATE'].dt.month
        # Drop the 'DATE' column
        df.drop(columns=['DATE'], inplace=True)
        # Update column names in the DataFrame
        df.columns = monthly_columns_with_data + ['Month']
        # Define the column to be shifted
        column_to_shift = 'Month'
        # Extract the column and delete it from DataFrame
        column = df[column_to_shift]
        del df[column_to_shift]
        # Insert the column at the first position
        df.insert(0, column_to_shift, column)
        # Output the prepared dataframe to a CSV file
        output_file_path = os.path.join('data', 'prepared', f"prepared_{locs_id}.csv")
        df.to_csv(output_file_path, index=False)
        # Remove 'Monthly' prefix from column names
        monthly_columns_with_data = [col.replace('Monthly', '') for col in monthly_columns_with_data]
        # Output the list of columns with non-empty 'Monthly' values to a txt file
        relevant_fields_file_path = os.path.join('data', 'prepared', f"relevant_fields_{locs_id}.txt")
        with open(relevant_fields_file_path, 'w') as file:
            file.write(", ".join(monthly_columns_with_data))
        
if __name__ == "__main__":
    # Load parameters from params.yaml
    with open('params/params.yaml', 'r') as file:
        params = yaml.safe_load(file)
    # Call prepare_data function with params
    prepare_data(params)
