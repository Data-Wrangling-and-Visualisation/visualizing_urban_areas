import pandas as pd
import os
from pathlib import Path

def filter_unnamed_entities(input_file, output_file=None):
    """
    Filter out unnamed entities from a CSV file.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str, optional): Path to save the filtered data. If None, will overwrite input file.
    """
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Filter out rows where Name is 'Unnamed'
    filtered_df = df[df['Name'] != 'Unnamed']
    
    # If no output file specified, overwrite the input file
    if output_file is None:
        output_file = input_file
    
    # Save the filtered data
    filtered_df.to_csv(output_file, index=False)
    print(f"Filtered data saved to {output_file}")
    print(f"Removed {len(df) - len(filtered_df)} unnamed entities")

if __name__ == "__main__":
    # Process only scraped_data.csv
    data_dir = Path(__file__).parent.parent / 'data'
    input_file = data_dir / 'scraped_data.csv'
    print(f"\nProcessing {input_file.name}...")
    filter_unnamed_entities(str(input_file),output_file = 'data/scraped_data_filtered.csv') 