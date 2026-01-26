import pandas as pd

def preprocess_data(df):
    # Drop useless columns
    df = df.drop(columns=["id", "dataset"])

    # Create binary target
    df["target"] = df["num"].apply(lambda x: 0 if x == 0 else 1)
    df = df.drop(columns=["num"])

    # Convert binary categorical values
    df["sex"] = df["sex"].map({"Male": 1, "Female": 0})
    df["fbs"] = df["fbs"].map({True: 1, False: 0})
    df["exang"] = df["exang"].map({True: 1, False: 0})

    # One-hot encode categorical features
    categorical_cols = ["cp", "restecg", "slope", "thal"]
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    return df


if __name__ == "__main__":
    df = pd.read_csv("../data/raw/heart_disease_uci.csv")
    processed_df = preprocess_data(df)

    print(processed_df.head())
    print(processed_df.info())
