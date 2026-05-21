import json
import pandas as pd

# 1. Load GeoJSON
with open("states_india.geojson", encoding="utf-8") as f:
    geo = json.load(f)
geojson_states = sorted([feature['properties']['st_nm'] for feature in geo['features']])

# 2. Load CSV
df = pd.read_csv("governance_master_final.csv")
csv_states = df['State'].unique()

print("\n🚨 DIAGNOSTIC REPORT 2.0 🚨")
print("===========================")

# Print J&K Data (Removed Utilization so it doesn't crash)
print("\n1. JAMMU & KASHMIR DATA IN CSV:")
jk_data = df[df['State'].str.contains('Jammu', case=False, na=False)]
if jk_data.empty:
    print(" ❌ Jammu & Kashmir is completely missing from your CSV!")
else:
    print(jk_data[['Scheme', 'State', 'Funds_Allocated', 'Funds_Spent']])

print("\n2. EXACT NAMES INSIDE THE MAP (GEOJSON):")
# Let's find exactly how the map spells the missing states
for s in geojson_states:
    if 'Jammu' in s or 'Kashmir' in s or 'J&K' in s:
        print(f" -> Map calls J&K: '{s}'")
    if 'Arunachal' in s:
        print(f" -> Map calls Arunachal: '{s}'")
    if 'Andaman' in s:
        print(f" -> Map calls Andaman: '{s}'")
    if 'Dadra' in s or 'Daman' in s:
        print(f" -> Map calls Dadra/Daman: '{s}'")
    if 'Ladakh' in s:
        print(f" -> Map calls Ladakh: '{s}'")