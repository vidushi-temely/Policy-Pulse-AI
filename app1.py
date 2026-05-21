import pandas as pd
import numpy as np

# ==========================================
# 1. STANDARDIZE STATE NAMES
# ==========================================
# This ensures all datasets use the exact same state names so the map doesn't break
state_mapping = {
    "Andaman and Nicobar Islands": "Andaman & Nicobar Islands",
    "Andhra Pradesh": "Andhra Pradesh", "Arunachal Pradesh": "Arunachal Pradesh",
    "Assam": "Assam", "Bihar": "Bihar", "Chandigarh": "Chandigarh",
    "Chhattisgarh": "Chhattisgarh", "Chattisgarh": "Chhattisgarh",
    "Dadra and Nagar Haveli and Daman and Diu": "Dadra & Nagar Haveli and Daman & Diu",
    "Dadra and Nagar Haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "Daman and Diu": "Dadra & Nagar Haveli and Daman & Diu",
    "Goa": "Goa", "Gujarat": "Gujarat", "Haryana": "Haryana",
    "Himachal Pradesh": "Himachal Pradesh", "Jammu and Kashmir": "Jammu & Kashmir",
    "Jammu & Kashmir": "Jammu & Kashmir", "Jharkhand": "Jharkhand",
    "Karnataka": "Karnataka", "Kerala": "Kerala", "Ladakh": "Ladakh",
    "Lakshadweep": "Lakshadweep", "Madhya Pradesh": "Madhya Pradesh",
    "Maharashtra": "Maharashtra", "Manipur": "Manipur", "Meghalaya": "Meghalaya",
    "Mizoram": "Mizoram", "Nagaland": "Nagaland", "Odisha": "Odisha",
    "Puducherry": "Puducherry", "Punjab": "Punjab", "Rajasthan": "Rajasthan",
    "Sikkim": "Sikkim", "Tamil Nadu": "Tamil Nadu", "Telangana": "Telangana",
    "Tripura": "Tripura", "Uttar Pradesh": "Uttar Pradesh", "Uttarakhand": "Uttarakhand",
    "West Bengal": "West Bengal", "Delhi": "NCT of Delhi"
}

def clean_state(name):
    if not isinstance(name, str): return name
    return state_mapping.get(name.strip().title(), name.strip())

# ==========================================
# 2. PROCESS AYUSHMAN BHARAT
# ==========================================
print("Processing Ayushman Bharat Data...")
df_ay_ben = pd.read_csv("RS_Session_266_AU_1728_A_to_C_7_ii.csv")
df_ay_fin = pd.read_csv("RS_Session_267_AS_121_A_to_B_ii.csv")

df_ay_ben['State'] = df_ay_ben['State/UT'].apply(clean_state)
df_ay_fin['State'] = df_ay_fin['State/UT'].apply(clean_state)

ayushman = pd.merge(
    df_ay_ben[['State', '2024-25']].rename(columns={'2024-25': 'Beneficiaries'}),
    df_ay_fin[['State', 'Central Release', 'Expenditure']].rename(columns={'Central Release': 'Funds_Allocated', 'Expenditure': 'Funds_Spent'}),
    on='State', how='outer'
)
ayushman['Scheme'] = 'Ayushman Bharat'

# ==========================================
# 3. PROCESS PM AWAS YOJANA (PMAY)
# ==========================================
print("Processing PM Awas Yojana Data...")
df_pmay = pd.read_csv("RS_Session_265_AU_701_A_to_D_i.csv")
df_pmay['State'] = df_pmay['State/ UT'].apply(clean_state)

pmay = df_pmay[[
    'State', 
    'Physical Progress of Houses (Nos) - Completed/ Delivered',
    'Financial Progress in respect of Central Assistance ( in Crore) - Sanctioned',
    'Financial Progress in respect of Central Assistance ( in Crore) - Released'
]].copy()

pmay.columns = ['State', 'Beneficiaries', 'Funds_Allocated', 'Funds_Spent']
pmay['Scheme'] = 'PM Awas Yojana'

# ==========================================
# 4. PROCESS PM KISAN
# ==========================================
print("Processing PM Kisan Data...")
# Using the clean_data.csv you provided which already has the metrics
df_kisan = pd.read_csv("clean_data.csv")
df_kisan['State'] = df_kisan['State'].apply(clean_state)

kisan = df_kisan[['State', 'Beneficiaries', 'Funds_Allocated', 'Funds_Spent']].copy()
kisan['Scheme'] = 'PM Kisan'

# ==========================================
# 5. PROCESS NFHS-5 CONTEXT DATA
# ==========================================
print("Processing NFHS Context Data...")
df_nfhs = pd.read_csv("datafile.csv")
ins_col = "Households with any usual member covered under a health insurance/financing scheme (%)"

df_nfhs['State'] = df_nfhs['States/UTs'].apply(clean_state)
# NFHS has Urban/Rural splits, so we take the mean for the state overall
nfhs = df_nfhs.groupby('State')[ins_col].apply(lambda x: pd.to_numeric(x, errors='coerce').mean()).reset_index()
nfhs.columns = ['State', 'Insurance_Coverage_Percent']

# ==========================================
# 6. FINAL CONSOLIDATION & CLEANUP
# ==========================================
print("Consolidating Master Dataset...")
# Stack all schemes on top of each other
master = pd.concat([ayushman, pmay, kisan], ignore_index=True)

# Map the NFHS context data to the master file
master = pd.merge(master, nfhs, on='State', how='left')

# Remove any "Total" rows or unmatched N/A states
master = master[~master['State'].str.contains('Total|India|Sub- total', case=False, na=False)]

# Fill missing numerical values with 0
master = master.fillna({
    'Beneficiaries': 0, 
    'Funds_Allocated': 0, 
    'Funds_Spent': 0, 
    'Insurance_Coverage_Percent': 0
})

# Add reporting year
master['Year'] = 2025

# Save to CSV
output_filename = "governance_master_final.csv"
master.to_csv(output_filename, index=False)

print(f"✅ Success! Master File '{output_filename}' created successfully.")
print("\n--- Data Summary ---")
print(master.groupby('Scheme').size().reset_index(name='State Count'))