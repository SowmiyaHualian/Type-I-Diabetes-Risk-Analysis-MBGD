import pandas as pd

df1 = pd.read_csv(r"../data/diabetes.csv")
df2 = pd.read_csv(r"../data/diabetes_data.csv")
df3 = pd.read_csv(r"../data/diabetes_data_upload.csv")
df4 = pd.read_csv(r"../data/diabetes_prediction_dataset.csv")


def standardize_columns(df):
    return df.rename(columns={
        # Age
        "Age": "Age",
        "age": "Age",

        # BMI / Obesity
        "BMI": "BMI",
        "bmi": "BMI",
        "Obesity": "BMI",

        # Glucose
        "Glucose": "Glucose",
        "blood_glucose_level": "Glucose",
        "FastingBloodSugar": "Glucose",

        # Insulin / HbA1c
        "Insulin": "Insulin",
        "HbA1c": "Insulin",
        "HbA1c_level": "Insulin",

        # Outcome / Target
        "Outcome": "Outcome",
        "Diagnosis": "Outcome",
        "class": "Outcome",
        "diabetes": "Outcome"
    })

df1 = standardize_columns(df1)
df2 = standardize_columns(df2)
df3 = standardize_columns(df3)
df4 = standardize_columns(df4)


required_columns = ["Age", "BMI", "Glucose", "Insulin", "Outcome"]

def select_required_columns(df):
    for col in required_columns:
        if col not in df.columns:
            df[col] = pd.NA
    return df[required_columns]

df1 = select_required_columns(df1)
df2 = select_required_columns(df2)
df3 = select_required_columns(df3)
df4 = select_required_columns(df4)


datasets = [df1, df2, df3, df4]

for df in datasets:
    df.fillna(df.median(numeric_only=True), inplace=True)

final_df = pd.concat(datasets, ignore_index=True)

final_df["Outcome"] = final_df["Outcome"].replace({
    "Positive": 1,
    "Negative": 0,
    "Yes": 1,
    "No": 0,
    True: 1,
    False: 0
})
# Convert to numeric safely
final_df["Outcome"] = pd.to_numeric(final_df["Outcome"], errors="coerce")

# Drop rows where Outcome is still invalid
final_df.dropna(subset=["Outcome"], inplace=True)

# Convert to int
final_df["Outcome"] = final_df["Outcome"].astype(int)

final_df.to_csv(r"../data/final_diabetes_dataset.csv", index=False)

print("✅ Dataset preprocessing completed successfully!")
print("Final dataset shape:", final_df.shape)
print("Columns used:", final_df.columns.tolist())
print("\nSample data:")
print(final_df.head())
