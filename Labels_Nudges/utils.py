import os
import pandas as pd
import glob
from django.conf import settings
from datetime import datetime


def get_final_articles():
    """
    Reads the latest final_manipulated CSV file (based on filename pattern)
    from the News_Processing/data folder and returns a list of article dictionaries.
    """
    # Construct the path using BASE_DIR:
    base_dir = os.path.join(settings.BASE_DIR, 'News_Processing', 'data')
    print("Looking in base directory:", base_dir)

    # Debug: List all files in that directory
    if os.path.exists(base_dir):
        print("Files in directory:", os.listdir(base_dir))
    else:
        print("Directory does not exist:", base_dir)

    # Use glob to find the CSV file(s)
    files = glob.glob(os.path.join(base_dir, "final_manipulated*.csv"))

    if not files:
        print("Final manipulated CSV not found.")
        return []

    # Choose the most recent file based on modification time
    latest_file = max(files, key=os.path.getmtime)
    print("Using file:", latest_file)

    # Read the CSV file with 'aid' as the index column
    df = pd.read_csv(latest_file, index_col='aid')
    # Convert DataFrame to a list of dictionaries
    articles = df.to_dict('records')
    return articles