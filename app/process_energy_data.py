# Importing necessary Libraries
import eurostat
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import PowerTransformer
import warnings

warnings.filterwarnings("ignore")

from notebooks.eurostat_dictionary import country_dictionary, energy_types_dict


def melt_and_sort(df, id_vars, value_name, sort_by, value_vars=None):
    # Use `pd.melt` to transform the DataFrame
    melted_df = pd.melt(df, id_vars=id_vars, var_name="year", value_name=value_name)

    # Convert 'year' to an integer type and sort the DataFrame
    melted_df["year"] = melted_df["year"].astype(int)
    melted_df = melted_df.sort_values(by=sort_by)

    return melted_df


def load_and_melt(code, id_vars, value_name, sort_by):
    # Load data using the eurostat API
    df = eurostat.get_data_df(code)

    # Melt and sort the DataFrame
    melted_df = melt_and_sort(df, id_vars, value_name, sort_by)

    return melted_df


def rename_columns(df):
    # Rename specific columns
    df.rename(columns={"geo\TIME_PERIOD": "geo", "siec": "energy_types"}, inplace=True)

    # Map 'geo' to 'country' using a dictionary
    df["country"] = df["geo"].replace(country_dictionary)

    # Map 'nrg_bal' to 'energy_use_types' using a dictionary
    df["energy_use_types"] = df["nrg_bal"].replace(energy_types_dict)

    # Rename unit columns
    df.rename(
        columns={"unit_x": "energy_unit", "unit_y": "household_unit"}, inplace=True
    )

    # Drop unnecessary columns
    columns_to_drop = ["nrg_bal", "geo", "freq"]
    df.drop(columns=columns_to_drop, inplace=True)

    return df


def filter_data(df):
    # Define a list of relevant energy use types
    energy_use_types = [
        "h_energy_use",
        "h_cooking",
        "h_space_heating",
        "h_water_heating",
        "h_space_cooling",
    ]

    # Filter DataFrame based on energy use types
    df = df[df["energy_use_types"].isin(energy_use_types)]

    # Filter DataFrame based on the year range
    df = df[(df["year"] >= 2012) & (df["year"] <= 2021)]

    # Filter DataFrame based on energy types containing 'TOTAL' (case-insensitive)
    columns_to_filter = ["energy_types", "agechild", "hhcomp", "n_child"]
    for column in columns_to_filter:
        df = df[df[column].str.contains("TOTAL", case=False)].reset_index(drop=True)

    return df


def preprocess_data(df, features):
    # Take out the missing values from the filtered dataset and use them for training models.
    train_df = df.dropna(
        subset=["energy_consumption"]
    )  # Rows with non-missing 'energy_consumption'

    # Selecting rows with missing values in the 'energy_consumption' column for prediction
    missing_values_to_predict = df[df["energy_consumption"].isnull()]

    # Scale energy_consumption for training data
    tscale = PowerTransformer()
    train_df["energy_consumption"] = tscale.fit_transform(
        train_df[["energy_consumption"]]
    )

    # Select relevant features for prediction on missing values
    selected_features_missing_values = missing_values_to_predict[features]

    # Convert categorical features to numeric using LabelEncoder for training
    labelencoder = LabelEncoder()
    train_df["country"] = labelencoder.fit_transform(train_df["country"])
    train_df["energy_use_types"] = labelencoder.fit_transform(
        train_df["energy_use_types"]
    )
    train_df["year"] = train_df["year"].astype("category")

    # Scale numerical features using PowerTransformer for training
    scaler = PowerTransformer()
    numerical_features = ["country", "number_of_households", "energy_use_types"]
    train_df[numerical_features] = scaler.fit_transform(train_df[numerical_features])

    # Convert categorical features to numeric using LabelEncoder for prediction data
    selected_features_missing_values["country"] = labelencoder.fit_transform(
        selected_features_missing_values["country"]
    )
    selected_features_missing_values["energy_use_types"] = labelencoder.fit_transform(
        selected_features_missing_values["energy_use_types"]
    )
    selected_features_missing_values["year"] = selected_features_missing_values[
        "year"
    ].astype("category")

    # Scale numerical features using the same scaler that was fit on the training data
    selected_features_missing_values[numerical_features] = scaler.transform(
        selected_features_missing_values[numerical_features]
    )

    return train_df, selected_features_missing_values, tscale, missing_values_to_predict


def train_and_predict_model(
    features,
    train_df,
    selected_features_missing_values,
    tscale,
    missing_values_to_predict,
):
    # Splitting features and target variable for train_df
    X = train_df[features]
    y = train_df["energy_consumption"]

    # Initialize the Decision Tree Regressor model for final prediction
    final_tree_model = DecisionTreeRegressor(
        max_depth=11, min_samples_split=2, random_state=42
    )

    # Train the model on the entire training data
    final_tree_model.fit(X, y)

    # Use the trained model to predict the missing values in the 'energy_consumption' column
    missing_values_predictions_scaled = final_tree_model.predict(
        selected_features_missing_values
    )

    # Inverse transform the scaled predictions to the original scale using target scaler
    missing_values_predictions_original_scale = tscale.inverse_transform(
        missing_values_predictions_scaled.reshape(-1, 1)
    )

    # Assign the unscaled predictions to the missing values prediction
    missing_values_to_predict[
        "energy_consumption"
    ] = missing_values_predictions_original_scale

    return missing_values_to_predict


def train_and_predict_model(
    features,
    train_df,
    selected_features_missing_values,
    tscale,
    missing_values_to_predict,
):
    # Splitting features and target variable for train_df
    X = train_df[features]
    y = train_df["energy_consumption"]

    # Initialize the Decision Tree Regressor model for final prediction
    final_tree_model = DecisionTreeRegressor(
        max_depth=11, min_samples_split=2, random_state=42
    )

    # Train the model on the entire training data
    final_tree_model.fit(X, y)

    # Use the trained model to predict the missing values in the 'energy_consumption' column
    missing_values_predictions_scaled = final_tree_model.predict(
        selected_features_missing_values
    )

    # Inverse transform the scaled predictions to the original scale using target scaler
    missing_values_predictions_original_scale = tscale.inverse_transform(
        missing_values_predictions_scaled.reshape(-1, 1)
    )

    # Assign the unscaled predictions to the missing values prediction
    missing_values_to_predict[
        "energy_consumption"
    ] = missing_values_predictions_original_scale

    return missing_values_to_predict


def process_and_predict_energy_consumption():
    """
    Load, process, and predict missing values in energy consumption data.
    """

    # Define common column names
    common_cols = ["freq", "geo\\TIME_PERIOD", "year"]

    # Load, process, and merge the DataFrames
    energy_df_melted = load_and_melt(
        "nrg_d_hhq",
        id_vars=["freq", "nrg_bal", "siec", "unit", "geo\\TIME_PERIOD"],
        value_name="energy_consumption",
        sort_by=common_cols,
    )

    household_melted_df = load_and_melt(
        "lfst_hhnhtych",
        id_vars=["freq", "agechild", "n_child", "hhcomp", "unit", "geo\\TIME_PERIOD"],
        value_name="number_of_households",
        sort_by=common_cols,
    )

    # Merge the melted DataFrames on common columns
    merged_df = pd.merge(energy_df_melted, household_melted_df, on=common_cols)

    # Apply the column renaming and data filtering functions
    merged_df = rename_columns(merged_df)
    filtered_df = filter_data(merged_df)

    # Imputing Number of household missing values with Median
    filtered_df["number_of_households"].fillna(
        filtered_df["number_of_households"].median(), inplace=True
    )

    # Selecting relevant features for prediction
    features = ["country", "number_of_households", "year", "energy_use_types"]
    (
        train_df,
        selected_features_missing_values,
        tscale,
        missing_values_to_predict,
    ) = preprocess_data(filtered_df, features)

    # Predict missing values in 'energy_consumption' using the Decision Tree Regressor model
    missing_values_to_predict = train_and_predict_model(
        features,
        train_df,
        selected_features_missing_values,
        tscale,
        missing_values_to_predict,
    )

    # Filling the missing data using common index in both DataFrames for the final dataset.
    filtered_df.loc[
        missing_values_to_predict.index, "energy_consumption"
    ] = missing_values_to_predict["energy_consumption"].values

    # Rename and keep energy data for model schema
    filtered_df.rename(
        columns={"country": "countries", "energy_unit": "units"}, inplace=True
    )

    train_df["year"] = train_df["year"].astype(int)

    enery_columns = [
        "countries",
        "energy_types",
        "energy_use_types",
        "year",
        "energy_consumption",
        "units",
    ]
    filtered_df = filtered_df[enery_columns]

    return filtered_df
