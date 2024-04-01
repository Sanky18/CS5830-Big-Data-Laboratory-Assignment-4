import pandas as pd
import os
import yaml

def process_data(params):
    # Load parameters from params.yaml
    locs_id = params['download']['locs_id']
    # Read the relevant fields from the txt file
    relevant_fields_file_path = os.path.join('data', 'prepared', f"relevant_fields_{locs_id}.txt")
    with open(relevant_fields_file_path, 'r') as file:
        relevant_fields = file.read().split(", ")
    # Read the CSV file containing the data
    csv_file_path = os.path.join('data', f"{locs_id}.csv")
    df = pd.read_csv(csv_file_path)
    # Filter out columns with names other than 'DATE' and starting with 'Daily'
    df = df.filter(regex=r'^DATE$|^Daily*')
    # Remove 'Daily' prefix from column names
    df.columns = df.columns.str.replace('Daily', '')
    # Rename specific columns
    df.rename(columns={
        'MaximumDryBulbTemperature': 'MaximumTemperature',
        'MinimumDryBulbTemperature': 'MinimumTemperature',
        'AverageDryBulbTemperature': 'MeanTemperature'
    }, inplace=True)
    # Select only the relevant columns
    relevant_columns = ['DATE'] + [col for col in df.columns if col in relevant_fields]
    df = df[relevant_columns]
    # Delete rows with any missing values
    df.dropna(inplace=True)
    # Convert DATE column to datetime
    df['DATE'] = pd.to_datetime(df['DATE'])
    # Extract month from the DATE column and create a new column 'Month'
    df['Month'] = df['DATE'].dt.month
    # Drop the 'DATE' column
    df.drop(columns=['DATE'], inplace=True)
    relevant_columns = df.columns
    # Convert all columns to numeric, coercing errors to NaN
    df = df.apply(pd.to_numeric, errors='coerce')
    # Compute averages based on 'Month'
    averages = df.groupby('Month').mean()
    # Reset index to make 'Month' a column instead of the index
    averages.reset_index(inplace=True)
    output_file_path = os.path.join('data', 'processed', f"processed_{locs_id}.csv")
    averages.to_csv(output_file_path, index=False)
    # Extract columns other than 'Month'
    required_columns = averages.columns[averages.columns != 'Month']
    # Write the column names to the file
    required_file_path = os.path.join('data', 'processed', f"required_{locs_id}.txt")
    with open(required_file_path, 'w') as file:
        file.write(", ".join(required_columns))
    
if __name__ == "__main__":
    # Load parameters from params.yaml
    with open('params/params.yaml', 'r') as file:
        params = yaml.safe_load(file)
    # Call process_data function with params
    process_data(params)
