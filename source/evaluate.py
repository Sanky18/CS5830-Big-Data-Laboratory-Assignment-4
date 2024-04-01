import pandas as pd
import os
import json
import yaml
from sklearn.metrics import r2_score

def compute_r2(params):
    # Load parameters from params.yaml
    locs_id = params['download']['locs_id']
    # Specify file paths
    prepared_file_path = os.path.join('data', 'prepared', f"prepared_{locs_id}.csv")
    processed_file_path = os.path.join('data', 'processed', f"processed_{locs_id}.csv")
    required_columns_file_path = os.path.join('data', 'processed', f"required_{locs_id}.txt")
    # Read prepared and processed CSV files
    prepared_df = pd.read_csv(prepared_file_path)
    processed_df = pd.read_csv(processed_file_path)
    # Read required columns from the required columns file
    with open(required_columns_file_path, 'r') as file:
        required_columns = file.read().split(", ")
    # Select only the relevant columns
    relevant_columns = ['Month'] + [col for col in prepared_df.columns if col in required_columns]
    # Filter columns in prepared_df
    prepared_df = prepared_df[relevant_columns]
    # Check if the number of rows in prepared_df is greater than processed_df
    if prepared_df.shape[0] > processed_df.shape[0]:
        # Find missing month numbers in processed_df
        missing_months = prepared_df[~prepared_df['Month'].isin(processed_df['Month'])]['Month']
        # Copy the entire row from prepared_df to processed_df for missing months
        for month in missing_months:
            missing_row = prepared_df[prepared_df['Month'] == month]
            processed_df = pd.concat([processed_df, missing_row], ignore_index=True)       
    # Check if the number of rows in processed_df is greater than prepared_df
    elif prepared_df.shape[0] < processed_df.shape[0]:
        # Find missing month numbers in prepared_df
        missing_months = processed_df[~processed_df['Month'].isin(prepared_df['Month'])]['Month']
        # Copy the entire row from processed_df to prepared_df for missing months
        for month in missing_months:
            missing_row = processed_df[processed_df['Month'] == month]
            prepared_df = pd.concat([prepared_df, missing_row], ignore_index=True)       
    # Sort both DataFrames by Month
    prepared_df.sort_values(by='Month', inplace=True)
    processed_df.sort_values(by='Month', inplace=True)
    # Compute R2 scores for each column
    r2_scores = {}
    for column in required_columns:
        r2 = r2_score(prepared_df[column], processed_df[column])
        r2_scores[column] = r2
    # Compute overall R2 using variance-weighted approach
    overall_r2 = r2_score(prepared_df[required_columns], processed_df[required_columns], multioutput='variance_weighted')
    # Save individual R2 scores and combined R2 to a JSON file
    output_file_path = os.path.join('output', f"r2.json")
    with open(output_file_path, 'a') as json_file:
        json_file.write(f'\n\n"{locs_id}.csv": ')  # Start a new line with {locs_id}
        json.dump({'individual_r2': r2_scores, 'combined_r2': overall_r2}, json_file)


if __name__ == "__main__":
    # Load parameters from params.yaml
    with open('params/params.yaml', 'r') as file:
        params = yaml.safe_load(file)
    # Call process_data function with params
    compute_r2(params)
