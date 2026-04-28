#s16798
#data loading file

import pandas as pd
import streamlit as st
from datetime import datetime


@st.cache_data
def load_data():

    #Load CSV File
    df = pd.read_csv("car_price_dataset .csv")

    #Remove extra spaces from column names
    df.columns = df.columns.str.strip()

    #Drop unnecessary index column if it exists
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")

    # Remove missing values and duplicate rows
    df= df.dropna().drop_duplicates().copy()

    ########Feature Engineering############################################

    # Convert Date column to datetime format
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    #Create new feature: Age of vehicle
    df["Age"]  = 2025 - df["YOM"]

    # Convert availability features into binary variables (0 or 1)
    for col in ["AIR CONDITION","POWER STEERING","POWER MIRROR","POWER WINDOW"]:
        df[col + "_bin"] = (df[col] == "Available").astype(int)

    # Additional binary feature conversions
    df["Leasing_bin"]   = (df["Leasing"] != "No Leasing").astype(int)
    df["Gear_bin"]      = (df["Gear"] == "Automatic").astype(int)
    df["Condition_bin"] = (df["Condition"] == "NEW").astype(int)
     
    # Standardize text columns (remove spaces & fix formatting)
    for col in ["Brand", "Model", "Town"]:
        df[col] = df[col].astype(str).str.strip().str.title()
    # Remove rows with empty Brand or Model
    df = df[(df["Brand"] != "") & (df["Model"] != "")]


    #Province Mapping (Sri Lanka Locations)
    town_to_province = {
        "Colombo":"Western","Gampaha":"Western","Negombo":"Western",
        "Kalutara":"Western","Panadura":"Western","Moratuwa":"Western",
        "Dehiwala-Mount-Lavinia":"Western","Maharagama":"Western",
        "Kotte":"Western","Wattala":"Western","Ja-Ela":"Western",
        "Kelaniya":"Western","Kadawatha":"Western","Nugegoda":"Western",
        "Piliyandala":"Western","Boralesgamuwa":"Western",
        "Kandy":"Central","Matale":"Central","Nuwara-Eliya":"Central",
        "Gampola":"Central","Nawalapitiya":"Central","Hatton":"Central",
        "Galle":"Southern","Matara":"Southern","Hambantota":"Southern",
        "Weligama":"Southern","Tangalle":"Southern","Hikkaduwa":"Southern",
        "Ambalangoda":"Southern","Jaffna":"Northern","Vavuniya":"Northern",
        "Kilinochchi":"Northern","Mullaitivu":"Northern",
        "Batticaloa":"Eastern","Trincomalee":"Eastern","Ampara":"Eastern",
        "Kalmunai":"Eastern","Kurunegala":"North Western","Puttalam":"North Western",
        "Kuliyapitiya":"North Western","Chilaw":"North Western",
        "Anuradapura":"North Central","Polonnaruwa":"North Central",
        "Badulla":"Uva","Bandarawela":"Uva","Haputale":"Uva","Welimada":"Uva",
        "Ratnapura":"Sabaragamuwa","Kegalle":"Sabaragamuwa","Balangoda":"Sabaragamuwa"
    }
    df["Province"] = df["Town"].map(town_to_province).fillna("Other")

    #engine segments
    # The Engine_Segment categories are currently fixed based on CC ranges:
    # Micro (<800cc), Compact (800-1200cc), Mid-Range (1200-1600cc), Large (>1600cc),
    # Unknown for missing values.
    # LIMITATION: These ranges are hard-coded and cannot be adjusted by users via the web app.
    def segment_engine(cc):
        if pd.isna(cc):
            return "Unknown"
        elif cc < 800:
            return "Micro"
        elif 800 <= cc <= 1200:
            return "Compact"
        elif 1200 < cc <= 1600:
            return "Mid-Range"
        elif cc > 1600:
            return "Large"
        else:
            return "Unknown"

    df["Engine_Segment"] = df["Engine (cc)"].apply(segment_engine)

    # Remove Town column
    df = df.drop(columns=["Town"])

    return df