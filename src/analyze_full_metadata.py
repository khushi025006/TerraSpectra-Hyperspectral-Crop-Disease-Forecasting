from pathlib import Path
import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
METADATA_PATH = PROJECT_ROOT / "data" / "raw" / "metadata.tab"
REPORT_PATH = PROJECT_ROOT / "reports" / "full_metadata_analysis.txt"

print("\n" + "=" * 60)
print("TERRASPECTRA - FULL DATASET METADATA ANALYSIS")
print("=" * 60)

# Load metadata
df = pd.read_csv(
    METADATA_PATH,
    sep="\t",
    dtype=str,
    na_values=["NA", ""],
    keep_default_na=True
)

# Clean column names and values
df.columns = df.columns.str.strip()

for column in df.columns:
    df[column] = df[column].str.strip().str.strip('"')

# Convert data types
df["image_id"] = pd.to_numeric(df["image_id"], errors="coerce")
df["trial"] = pd.to_numeric(df["trial"], errors="coerce")
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Identify plant groups
df["plant_group"] = df["plant"].str.split("/").str[0]

# Identify repeated objects
object_columns = ["trial", "plant", "leaf", "part"]
df["object_id"] = df[object_columns].fillna("UNKNOWN").astype(str).agg("_".join, axis=1)

# Basic information
print("\n1. DATASET OVERVIEW")
print("-" * 40)
print("Total records:", len(df))
print("Total columns:", len(df.columns))
print("Columns:", list(df.columns))

print("\n2. PLANT GROUP COUNTS")
print("-" * 40)
print(df["plant_group"].value_counts(dropna=False))

print("\n3. TRIAL COUNTS")
print("-" * 40)
print(df["trial"].value_counts().sort_index())

print("\n4. DATE INFORMATION")
print("-" * 40)
print("First observation:", df["date"].min())
print("Last observation:", df["date"].max())
print("Unique observation dates:", df["date"].nunique())

print("\n5. REPEATED OBJECT ANALYSIS")
print("-" * 40)

object_counts = df.groupby("object_id").agg(
    observation_count=("image_id", "count"),
    unique_dates=("date", "nunique"),
    first_date=("date", "min"),
    last_date=("date", "max")
).reset_index()

repeated_objects = object_counts[
    object_counts["observation_count"] > 1
]

print("Unique plant/leaf/part objects:", len(object_counts))
print("Objects observed more than once:", len(repeated_objects))
print("Objects observed on multiple dates:",
      (object_counts["unique_dates"] > 1).sum())

print("\nTop 10 repeatedly observed objects:")
print(
    object_counts.sort_values(
        "observation_count", ascending=False
    ).head(10).to_string(index=False)
)

print("\n6. MISSING VALUES")
print("-" * 40)
print(df.isnull().sum())

print("\n7. SELECTED IMAGE CHECK")
print("-" * 40)

selected_ids = [1797, 1827, 1855]

selected = df[df["image_id"].isin(selected_ids)]

if selected.empty:
    print("Selected image IDs were not found in metadata.")
else:
    print(selected.to_string(index=False))

print("\n8. POSSIBLE DISEASE LABEL COLUMNS")
print("-" * 40)

label_columns = [
    col for col in df.columns
    if any(word in col.lower()
           for word in ["disease", "severity", "symptom", "infection", "label"])
]

if label_columns:
    print("Potential label columns:", label_columns)
else:
    print("No obvious disease-label columns found.")

# Save detailed report
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(REPORT_PATH, "w", encoding="utf-8") as file:
    file.write("TERRASPECTRA - FULL METADATA ANALYSIS\n")
    file.write("=" * 60 + "\n\n")

    file.write(f"Total records: {len(df)}\n")
    file.write(f"Total columns: {len(df.columns)}\n")
    file.write(f"Unique dates: {df['date'].nunique()}\n")
    file.write(f"First date: {df['date'].min()}\n")
    file.write(f"Last date: {df['date'].max()}\n\n")

    file.write("PLANT GROUP COUNTS\n")
    file.write(df["plant_group"].value_counts(dropna=False).to_string())
    file.write("\n\nTRIAL COUNTS\n")
    file.write(df["trial"].value_counts().sort_index().to_string())

    file.write("\n\nREPEATED OBJECT ANALYSIS\n")
    file.write(f"\nUnique objects: {len(object_counts)}")
    file.write(f"\nRepeated objects: {len(repeated_objects)}")
    file.write(
        f"\nObjects on multiple dates: "
        f"{(object_counts['unique_dates'] > 1).sum()}"
    )

    file.write("\n\nMISSING VALUES\n")
    file.write(df.isnull().sum().to_string())

    file.write("\n\nPOSSIBLE LABEL COLUMNS\n")
    file.write(str(label_columns))

# Save repeated-object details separately
object_counts.to_csv(
    PROJECT_ROOT / "reports" / "repeated_object_analysis.csv",
    index=False
)

print("\n" + "=" * 60)
print("ANALYSIS COMPLETED SUCCESSFULLY")
print("Report saved:", REPORT_PATH)
print("Repeated-object CSV saved in reports/")
print("=" * 60)