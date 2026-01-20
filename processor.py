import pandas as pd
import re
import numpy as np

def clean_product_name(text):
    """
    Uses Regex to remove technical IDs and noise before the #&AMP; string.
    If #&AMP; is not found, returns the original text stripped.
    Example: 'CH00016#&AMP;FABRIC...' becomes 'FABRIC...'
    """
    if pd.isna(text):
        return ""
    
    text_str = str(text)
    # The requirement specifies removing noise BEFORE the #&AMP; string.
    # We use a regex that matches everything from the start up to and including #&AMP;
    # We handle both #&AMP; and #& as the example in the prompt used #& but the text said #&AMP;
    pattern = r'^.*?#&(?:AMP;)?'
    cleaned = re.sub(pattern, '', text_str)
    return cleaned.strip()

def standardize_data(df_raw, df_targets):
    """
    Transforms raw trade data into a standardized business report.
    1. Filters 'Importer' against 'COMPANY NAME' in df_targets.
    2. Cleans 'Product' names using regex.
    3. Calculates 'Unit PRICE' (Value/Quantity) rounded to 2 decimal places.
    4. Maps to exactly 11 columns in the required order.
    """
    # Create a copy to avoid SettingWithCopyWarning
    df = df_raw.copy()
    
    # Clean column names (remove whitespace)
    df.columns = [col.strip() for col in df.columns]
    
    # 1. Target Filtering
    if 'Importer' in df.columns and df_targets is not None and 'COMPANY NAME' in df_targets.columns:
        valid_importers = df_targets['COMPANY NAME'].unique()
        df = df[df['Importer'].isin(valid_importers)].copy()
    
    # 2. Data Cleaning: Product Name
    if 'Product' in df.columns:
        df['Product'] = df['Product'].apply(clean_product_name)
    
    # 3. Calculation: Unit PRICE = Value / Quantity
    # Handle division by zero and nulls by returning 0
    if 'Value' in df.columns and 'Quantity' in df.columns:
        # Convert to numeric, error='coerce' turns non-numeric into NaN
        val = pd.to_numeric(df['Value'], errors='coerce').fillna(0)
        qty = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        
        # Vectorized calculation
        # np.where(condition, if_true, if_false)
        df['Unit PRICE'] = np.where(qty != 0, val / qty, 0.0)
        df['Unit PRICE'] = df['Unit PRICE'].round(2)
    else:
        df['Unit PRICE'] = 0.0
        
    # 4. Schema Mapping (Exact ordering of 11 columns)
    target_columns = [
        'Date', 'Origin Country', 'Exporter', 'Importer', 'HsCode', 
        'Product', 'Quantity', 'QuantityUnit', 'Value', 'ValueUnit', 'Unit PRICE'
    ]
    
    # Ensure all target columns exist in the dataframe
    for col in target_columns:
        if col not in df.columns:
            df[col] = None
            
    return df[target_columns]

def filter_by_product(df, search_query):
    """
    Dynamic search mechanism for sub-string searching (case-insensitive) within 'Product'.
    """
    if not search_query or pd.isna(search_query) or str(search_query).strip() == "":
        return df
    
    # Ensure Product column is string type for searching
    return df[df['Product'].astype(str).str.contains(search_query, case=False, na=False)]
