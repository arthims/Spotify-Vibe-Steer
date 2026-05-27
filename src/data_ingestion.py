import os
import pandas as pd
from datasets import load_dataset
import pyarrow as pa
import pyarrow.parquet as pq

def ingest_data():
    print("Loading dataset from Hugging Face...")
    try:
        # Load the dataset
        dataset = load_dataset("ManikaSaini/zomato-restaurant-recommendation")
        # Most HF datasets use 'train' split by default
        df = dataset['train'].to_pandas()
        print(f"Dataset loaded. Shape: {df.shape}")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    print("Preprocessing data...")
    
    # Lowercase column names for easier access
    df.columns = [col.lower() for col in df.columns]
    
    # CRITICAL FIX for Streamlit Cloud: Drop massive text columns to prevent Out-Of-Memory (OOM) crashes
    heavy_cols = ['reviews_list', 'menu_item', 'dish_liked', 'url', 'phone', 'address']
    df = df.drop(columns=[col for col in heavy_cols if col in df.columns], errors='ignore')
    
    # Ensure critical columns exist. Let's use flexible names.
    name_col = 'name' if 'name' in df.columns else 'restaurant name' if 'restaurant name' in df.columns else None
    loc_col = 'location' if 'location' in df.columns else 'city' if 'city' in df.columns else None
    cuisine_col = 'cuisines' if 'cuisines' in df.columns else 'cuisine' if 'cuisine' in df.columns else None
    cost_col = 'cost' if 'cost' in df.columns else 'approx cost(for two people)' if 'approx cost(for two people)' in df.columns else 'cost for two' if 'cost for two' in df.columns else None
    rate_col = 'rate' if 'rate' in df.columns else 'rating' if 'rating' in df.columns else None

    # Drop rows missing crucial identifiers if possible
    if name_col and loc_col and cuisine_col:
        df = df.dropna(subset=[name_col, loc_col, cuisine_col])
    else:
        print("Warning: Missing some standard columns, skipping basic dropna")

    # Clean Cost
    if cost_col and df[cost_col].dtype == object:
        df[cost_col] = df[cost_col].astype(str).str.replace(',', '', regex=False).str.extract(r'(\d+)').astype(float)
    
    # Clean Rating
    if rate_col and df[rate_col].dtype == object:
        # Sometimes ratings look like "4.1/5" or "NEW"
        df[rate_col] = df[rate_col].astype(str).str.split('/').str[0]
        df[rate_col] = pd.to_numeric(df[rate_col], errors='coerce').fillna(0)
    
    # Standardize textual categories
    if cuisine_col:
        df[cuisine_col] = df[cuisine_col].astype(str).str.lower()
    if loc_col:
        df[loc_col] = df[loc_col].astype(str).str.lower()

    # Determine output directory (project root -> data)
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'cleaned_zomato.parquet')

    # Save to Parquet
    print(f"Saving cleaned dataset to {output_file}...")
    df.to_parquet(output_file, index=False)
    print("Data ingestion and preprocessing complete!")

if __name__ == "__main__":
    ingest_data()
