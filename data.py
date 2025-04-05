import pandas as pd
import streamlit as st

def load_dataset():
    try:
        df = pd.read_csv("flights_subset_40.csv")
        if df.empty:
            st.error("Error: Dataset 'flights_subset_40.csv' is empty!")
            return None
        return df
    except FileNotFoundError:
        st.error("Error: 'flights_subset_40.csv' not found!")
        return None

def search_flights(departure_city, destination, travel_date, df):
    if df is None or df.empty:
        return None
    # Case-insensitive and stripped search
    filtered = df[
        (df["Departure_City"].str.strip().str.lower() == departure_city.lower().strip()) &
        (df["Destination"].str.strip().str.lower() == destination.lower().strip()) &
        (df["Travel_Date"].str.strip() == travel_date.strip())
    ]
    return filtered.to_dict("records") if not filtered.empty else None