import pandas as pd
from processor import clean_product_name, standardize_data, filter_by_product

# 1. Test clean_product_name
test_text = "CH00016#&AMP;FABRIC 100% COTTON"
cleaned = clean_product_name(test_text)
print(f"Original: {test_text}")
print(f"Cleaned: {cleaned}")
assert cleaned == "FABRIC 100% COTTON"

# 2. Test standardize_data with dummy data
raw_data = {
    'Date': ['2026-01-01', '2026-01-02'],
    'Origin Country': ['China', 'Vietnam'],
    'Exporter': ['Exp1', 'Exp2'],
    'Importer': ['Target Corp', 'Other Corp'],
    'HsCode': ['1234', '5678'],
    'Product': ['Item1#&AMP;DESCR1', 'Item2#&AMP;DESCR2'],
    'Quantity': [100, 200],
    'QuantityUnit': ['PCS', 'PCS'],
    'Value': [1000, 4000],
    'ValueUnit': ['USD', 'USD']
}
df_raw = pd.DataFrame(raw_data)

target_data = {
    'COMPANY NAME': ['Target Corp', 'Expert Co']
}
df_targets = pd.DataFrame(target_data)

df_processed = standardize_data(df_raw, df_targets)

print("\nProcessed Data:")
print(df_processed)

# Check count (should be 1 because 'Other Corp' is filtered out)
assert len(df_processed) == 1
assert df_processed.iloc[0]['Importer'] == 'Target Corp'
assert df_processed.iloc[0]['Unit PRICE'] == 10.0
assert df_processed.iloc[0]['Product'] == 'DESCR1'

# 3. Test division by zero
df_zero = pd.DataFrame({
    'Importer': ['Target Corp'],
    'Quantity': [0],
    'Value': [100],
    'Product': ['Test']
})
# Re-running standardize_data with zero quantity
df_processed_zero = standardize_data(df_zero, df_targets)
print("\nProcessed Data with Zero Quantity:")
print(df_processed_zero)
assert df_processed_zero.iloc[0]['Unit PRICE'] == 0.0

# 4. Test filter_by_product
df_search = filter_by_product(df_processed, "descr")
print("\nSearch results for 'descr':")
print(df_search)
assert len(df_search) == 1

df_none = filter_by_product(df_processed, "XYZ")
print("\nSearch results for 'XYZ':")
print(df_none)
assert len(df_none) == 0

print("\nAll tests passed!")

