import os
import requests
import shutil
import yaml

def download_data(params):
    # Fetch parameters from params.yaml
    year = params['download']['year']
    locs_id = params['download']['locs_id']
    # Construct URL
    url = f"https://www.ncei.noaa.gov/data/local-climatological-data/access/{year}/{locs_id}.csv"
    # Create data directory if it doesn't exist
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    # Download the CSV file
    csv_file_path = os.path.join(data_dir, f'{locs_id}.csv')
    with requests.get(url, stream=True) as response:
        with open(csv_file_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
    

            
if __name__ == "__main__":
    # Load parameters from params.yaml
    with open('params/params.yaml', 'r') as file:
        params = yaml.safe_load(file)

    # Call download_data function with params
    download_data(params)

