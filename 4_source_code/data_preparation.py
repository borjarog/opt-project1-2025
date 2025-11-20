import os
import json
import sys
import pandas as pd
import re
import geopandas as gpd

input_data_path = os.path.join(
    os.path.dirname(__file__), "../2_data/raw/dataset.geojson"
)
output_data_path = os.path.join(
    os.path.dirname(__file__), "../2_data/processed/final_dataset.geojson"
)

# -------------------------------- #
#      1.Suitability variables     #
# -------------------------------- #

# Suitability score mapping dictionary
score_map = {
    "High": 3.0,
    "Moderate-High": 2.5,
    "Moderate": 2.0,
    "Low-Moderate": 1.5,
    "Low": 1.0,
    "Very Low": 0.0,
}
# Atelerix algirus
atelerix_rules = {
    "Discontinuous Urban Fabric": "Moderate",
    "Continuous Urban Fabric": "Low",
    "Industrial or Commercial Units": "Very Low",
    "Airports": "Very Low",
    "Port Areas": "Very Low",
    "Sport and Leisure Facilities": "Very Low",
    "Pastures": "High",
    "Non-irrigated Arable Land": "High",
    "Permanently Irrigated Land": "Low",
    "Complex Cultivation Patterns": "High",
    "Land Principally Occupied by Agriculture with Significant Areas of Natural Vegetation": "High",
    "Sclerophyllous Vegetation": "High",
    "Transitional Woodland-Shrub": "High",
    "Natural Grasslands": "Moderate-High",
    "Broad-leaved Forests": "Moderate",
    "Mixed Forests": "Moderate",
    "Coniferous Forests": "Low",
    "Peatbogs": "Very Low",
    "Inland Marshes": "Very Low",
    "Coastal Lagoons": "Very Low",
    "Estuaries": "Very Low",
    "Intertidal Flats": "Very Low",
    "Water Courses": "Low-Moderate",
}

# Martes martes
martes_rules = {
    "Discontinuous Urban Fabric": "Low",
    "Continuous Urban Fabric": "Very Low",
    "Industrial or Commercial Units": "Very Low",
    "Airports": "Very Low",
    "Port Areas": "Very Low",
    "Sport and Leisure Facilities": "Very Low",
    "Pastures": "Low",
    "Non-irrigated Arable Land": "Low",
    "Permanently Irrigated Land": "Very Low",
    "Complex Cultivation Patterns": "Moderate",
    "Land Principally Occupied by Agriculture with Significant Areas of Natural Vegetation": "Moderate-High",
    "Sclerophyllous Vegetation": "High",
    "Transitional Woodland-Shrub": "High",
    "Natural Grasslands": "Low-Moderate",
    "Broad-leaved Forests": "High",
    "Mixed Forests": "High",
    "Coniferous Forests": "Moderate-High",
    "Peatbogs": "Very Low",
    "Inland Marshes": "Very Low",
    "Coastal Lagoons": "Very Low",
    "Estuaries": "Very Low",
    "Intertidal Flats": "Very Low",
    "Water Courses": "Low-Moderate",
}

# Eliomys quercinus
eliomys_rules = {
    "Discontinuous Urban Fabric": "Low",
    "Continuous Urban Fabric": "Very Low",
    "Industrial or Commercial Units": "Very Low",
    "Airports": "Very Low",
    "Port Areas": "Very Low",
    "Sport and Leisure Facilities": "Very Low",
    "Pastures": "Low",
    "Non-irrigated Arable Land": "Low",
    "Permanently Irrigated Land": "Very Low",
    "Complex Cultivation Patterns": "Moderate",
    "Land Principally Occupied by Agriculture with Significant Areas of Natural Vegetation": "Moderate-High",
    "Sclerophyllous Vegetation": "High",
    "Transitional Woodland-Shrub": "High",
    "Natural Grasslands": "Low",
    "Broad-leaved Forests": "High",
    "Mixed Forests": "High",
    "Coniferous Forests": "Moderate-High",
    "Peatbogs": "Very Low",
    "Inland Marshes": "Very Low",
    "Coastal Lagoons": "Very Low",
    "Estuaries": "Very Low",
    "Intertidal Flats": "Very Low",
    "Water Courses": "Low-Moderate",
}

# Oryctolagus cuniculus
oryctolagus_rules = {
    "Discontinuous Urban Fabric": "Low",
    "Continuous Urban Fabric": "Very Low",
    "Industrial or Commercial Units": "Very Low",
    "Airports": "Very Low",
    "Port Areas": "Very Low",
    "Sport and Leisure Facilities": "Very Low",
    "Pastures": "High",
    "Non-irrigated Arable Land": "High",
    "Permanently Irrigated Land": "Low",
    "Complex Cultivation Patterns": "High",
    "Land Principally Occupied by Agriculture with Significant Areas of Natural Vegetation": "High",
    "Sclerophyllous Vegetation": "High",
    "Transitional Woodland-Shrub": "High",
    "Natural Grasslands": "High",
    "Broad-leaved Forests": "Moderate",
    "Mixed Forests": "Moderate",
    "Coniferous Forests": "Low-Moderate",
    "Peatbogs": "Very Low",
    "Inland Marshes": "Very Low",
    "Coastal Lagoons": "Very Low",
    "Estuaries": "Very Low",
    "Intertidal Flats": "Very Low",
    "Water Courses": "Low",
}

# -------------------------------- #
#        2.Human disturbance       #
# -------------------------------- #

human_disturbance_map = {
    # ---  Urban and Industrial Areas (High Risk) ---
    "Continuous Urban Fabric": 1.0,
    "Industrial or Commercial Units": 1.0,
    "Airports": 1.0,
    "Port Areas": 1.0,
    "Discontinuous Urban Fabric": 0.7,
    "Sport and Leisure Facilities": 0.6,
    # --- Agriculture (Medium/Low Risk) ---
    "Permanently Irrigated Land": 0.5,
    "Unknown": 0.5,
    "Non-irrigated Arable Land": 0.3,
    "Complex Cultivation Patterns": 0.2,
    "Land Principally Occupied by Agriculture with Significant Areas of Natural Vegetation": 0.1,
    # --- Nature and Forests (No Risk) ---
    "Pastures": 0.1,
    "Broad-leaved Forests": 0.0,
    "Sclerophyllous Vegetation": 0.0,
    "Mixed Forests": 0.0,
    "Transitional Woodland-Shrub": 0.0,
    "Natural Grasslands": 0.0,
    "Coniferous Forests": 0.0,
    "Peatbogs": 0.0,
    "Inland Marshes": 0.0,
    "Coastal Lagoons": 0.0,
    "Estuaries": 0.0,
    "Intertidal Flats": 0.0,
    # --- Water ---
    "Water Courses": 0.1,
}

# -------------------------------- #
#       3.Auxiliary Functions      #
# -------------------------------- #


# Load GeoJSON dataset
def load_geojson(filepath):
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)

    gdf = gpd.read_file(filepath)
    print(f"[INFO] Loaded dataset: {len(gdf)} cells.")
    return gdf


# Function to get suitability score for a given land cover type and species rules
def get_suitability_score(land_cover, rules_dict):
    text_val = rules_dict.get(land_cover, "Very Low")
    return score_map.get(text_val, 0.0)


# Extract grid coordinates from grid_id
def extract_coords(grid_id):
    # Convert 'cell_12_34' in tupple (12, 34)
    match = re.match(r"cell_(\d+)_(\d+)", grid_id)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0


def get_neighbors_str(row, all_ids_set):
    # Returns string 'cell_0_1,...' with valid neighbors (8-connected).
    x, y = row["grid_x"], row["grid_y"]

    candidates = [
        # Cross
        f"cell_{x}_{y + 1}",  # Up
        f"cell_{x}_{y - 1}",  # Down
        f"cell_{x - 1}_{y}",  # Left
        f"cell_{x + 1}_{y}",  # Right
        # Diagonals
        f"cell_{x - 1}_{y + 1}",  # Up-Left
        f"cell_{x + 1}_{y + 1}",  # Up-Right
        f"cell_{x - 1}_{y - 1}",  # Down-Left
        f"cell_{x + 1}_{y - 1}",  # Down-Right
    ]

    valid = [c for c in candidates if c in all_ids_set]
    return ",".join(valid)


def data_preparation(df):
    print("[INFO] Processing new variables...")

    # 3.1 Grid Coordinates
    df["grid_x"], df["grid_y"] = zip(*df["grid_id"].apply(extract_coords))

    # 3.2 Neighbors
    all_ids = set(df["grid_id"])
    df["neighbors"] = df.apply(lambda row: get_neighbors_str(row, all_ids), axis=1)

    # 3.3 Human Disturbance
    df["human_disturbance"] = (
        df["dominant_land_cover_name"].map(human_disturbance_map).fillna(0.5)
    )

    # 3.4 Current Richness
    species_cols = [c for c in df.columns if c.startswith("has_")]
    df["current_richness"] = df[species_cols].sum(axis=1).astype(int)

    print("[INFO] Processing variables for each species...")

    species_config = [
        ("atelerix", atelerix_rules),
        ("martes", martes_rules),
        ("eliomys", eliomys_rules),
        ("oryctolagus", oryctolagus_rules),
    ]

    for name, rules in species_config:
        # A. Suitability Score (0-3)
        df[f"suitability_{name}"] = df["dominant_land_cover_name"].apply(
            lambda x: get_suitability_score(x, rules)
        )

        # B. Efficiency (Suitability / Cost)
        cost_col = f"cost_adaptation_{name}"
        suit_col = f"suitability_{name}"
        if cost_col in df.columns:
            df[f"efficiency_{name}"] = df[suit_col] / (df[cost_col] + 0.01)

    return df


if __name__ == "__main__":
    print("--- START OF DATA PREPARATION ---")

    # 1. Load
    if not os.path.exists(input_data_path):
        print(f"[ERROR] File not found: {input_data_path}")
        sys.exit(1)

    df_raw = load_geojson(input_data_path)

    # 2. Transform
    df_clean = data_preparation(df_raw)

    # 3. Save

    # A. Save GeoJSON (Keep geometry for mapping)
    print(f"[INFO] Saving GeoJSON: {output_data_path}")
    df_clean.to_file(output_data_path, driver="GeoJSON")

    # B. Save CSV (Remove geometry for optimization)
    output_csv_path = output_data_path.replace(".geojson", ".csv")
    print(f"[INFO] Saving CSV in: {output_csv_path}")

    df_csv = pd.DataFrame(df_clean.drop(columns="geometry"))
    df_csv.to_csv(output_csv_path, index=False)

    print("\n--- PROCESS COMPLETED ---")
    print(
        f"Generated files:\n 1. {output_data_path} (With map)\n 2. {output_csv_path} (Only data)"
    )
