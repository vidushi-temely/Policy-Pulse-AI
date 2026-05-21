import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("clean_data.csv", encoding="latin1")
print(df.head())

# # Remove rows where State column has header text again
# df = df[df["State/UT"] != "State/UT"]

# # Remove rows where State is 'Total'
# df = df[df["State/UT"] != "Total"]

# # Get last column (latest data)
# latest_column = df.columns[-1]

# # Keep only needed columns
# df = df[["State/UT", latest_column]]

# # Rename columns
# df.columns = ["State", "Beneficiaries"]
# df = df.dropna()

# df["Beneficiaries"] = pd.to_numeric(df["Beneficiaries"], errors='coerce')
# df = df.dropna()

# df["Funds_Allocated"] = df["Beneficiaries"] * 0.03
# df["Funds_Spent"] = df["Funds_Allocated"] * 0.9

# df["Efficiency"] = df["Beneficiaries"] / df["Funds_Spent"]
# df["Utilization"] = (df["Funds_Spent"] / df["Funds_Allocated"]) * 100

# df.to_csv("clean_data.csv", index=False)

#____________________________



# Random variation in allocation (2% to 5%)
df["Funds_Allocated"] = df["Beneficiaries"] * np.random.uniform(0.02, 0.05, len(df))

# Random utilization (70% to 95%)
df["Funds_Spent"] = df["Funds_Allocated"] * np.random.uniform(0.7, 0.95, len(df))

df["Efficiency"] = df["Beneficiaries"] / df["Funds_Spent"]
df["Utilization"] = (df["Funds_Spent"] / df["Funds_Allocated"]) * 100

print(df)
# Best performing state
print("Best State:")
print(df.sort_values(by="Efficiency", ascending=False).head(1))

# Worst performing state
print("Worst State:")
print(df.sort_values(by="Efficiency").head(1))
print("\nUnderperforming States:")

for index, row in df.iterrows():
    if row["Efficiency"] < 200:
        print(row["State"], "is underperforming")


#matplotlib visualization

# Sort data for better visualization
df_sorted = df.sort_values(by="Efficiency", ascending=False)

colors = ["red" if x < 30 else "green" for x in df_sorted["Efficiency"]]

plt.figure(figsize=(12,6))
plt.bar(df_sorted["State"], df_sorted["Efficiency"], color=colors)

plt.xticks(rotation=90)
plt.title("Efficiency by State (Red = Low, Green = Good)")
plt.tight_layout()
plt.show()


def recommend_action(row):
    if row["Efficiency"] < 180:
        return "Improve implementation / investigate issues"
    elif row["Utilization"] < 70:
        return "Increase fund utilization"
    elif row["Efficiency"] > 250:
        return "High performing - can be model state"
    else:
        return "Normal performance"

df["Recommendation"] = df.apply(recommend_action, axis=1)

print(df[["State", "Efficiency", "Utilization", "Recommendation"]])





df["Rank"] = df["Efficiency"].rank(ascending=False)

df = df.sort_values(by="Rank")

print(df[["State", "Efficiency", "Rank"]])

critical = df[df["Efficiency"] < 180]

print("\nCritical States:")
print(critical[["State", "Efficiency"]])




# Top 10 states
df_sorted = df.sort_values(by="Efficiency", ascending=False).head(10)

# Color logic
colors = []
for x in df_sorted["Efficiency"]:
    if x < 30:
        colors.append("red")
    elif x < 40:
        colors.append("orange")
    else:
        colors.append("green")

# Plot
plt.figure(figsize=(10,5))
plt.bar(df_sorted["State"], df_sorted["Efficiency"], color=colors)

plt.title("Top 10 State Performance (Red=Poor, Orange=Avg, Green=Good)")
plt.xlabel("State")
plt.ylabel("Efficiency")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
print("Best State:", df_sorted.iloc[0]["State"])
print("Worst State:", df.sort_values(by="Efficiency").iloc[0]["State"])