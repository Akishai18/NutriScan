import pandas as pd
import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Property, DataType, Configure

print("Current working directory:", os.getcwd())

load_dotenv()
weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
google_project_id = os.environ["GOOGLE_PROJECT_ID"]

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)
assert client.is_ready(), "Weaviate connection failed."

df = pd.read_csv("data/nutrition4.csv")

if df.columns[0].startswith("Unnamed"):
    df = df.drop(columns=[df.columns[0]])

original_to_clean = {}
cleaned_cols = []
for col in df.columns:
    clean = col.strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
    if not clean[0].isalpha():
        clean = "col_" + clean
    original_to_clean[col] = clean
    cleaned_cols.append(clean)

df.columns = cleaned_cols

numeric_cols = [col for col in df.columns if col not in {"food_name", "category_name"}]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

text_cols = set(df.columns) - set(numeric_cols)
for col in text_cols:
    df[col] = df[col].fillna("")

descriptions = {
    "food_name": "Name of the food item",
    "category_name": "Category or group of the food",
    "calcium": "Amount of calcium in grams",
    "calories": "Energy content in kilocalories",
    "carbs": "Total carbohydrate content in grams",
    "cholesterol": "Cholesterol amount in grams",
    "copper": "Amount of copper in grams",
    "fats": "Total fat content in grams",
    "fiber": "Dietary fiber content in grams",
    "folate": "Amount of folate in grams",
    "iron": "Iron content in grams",
    "magnesium": "Magnesium content in grams",
    "monounsaturated_fat": "Monounsaturated fat content",
    "net_carbs": "Net carbohydrates (carbs minus fiber)",
    "omega_3_dha": "Amount of DHA Omega-3",
    "omega_3_dpa": "Amount of DPA Omega-3",
    "omega_3_epa": "Amount of EPA Omega-3",
    "phosphorus": "Phosphorus content in grams",
    "polyunsaturated_fat": "Polyunsaturated fat content",
    "potassium": "Potassium content in grams",
    "protein": "Protein content in grams",
    "saturated_fat": "Saturated fat content",
    "selenium": "Selenium amount",
    "sodium": "Sodium content in grams",
    "trans_fat": "Trans fat content",
    "vitamin_a_iu": "Vitamin A in international units (IU)",
    "vitamin_a_rae": "Vitamin A in retinol activity equivalents (RAE)",
    "vitamin_b1": "Thiamine (Vitamin B1) content",
    "vitamin_b2": "Riboflavin (Vitamin B2) content",
    "vitamin_b3": "Niacin (Vitamin B3) content",
    "vitamin_b5": "Pantothenic acid (Vitamin B5) content",
    "vitamin_b6": "Vitamin B6 content",
    "vitamin_b12": "Vitamin B12 content",
    "vitamin_c": "Vitamin C content",
    "vitamin_d": "Vitamin D content",
    "vitamin_e": "Vitamin E content",
    "vitamin_k": "Vitamin K content",
    "zinc": "Zinc content in grams",
    "choline": "Choline content",
    "fructose": "Fructose sugar amount",
    "histidine": "Amino acid: Histidine",
    "isoleucine": "Amino acid: Isoleucine",
    "leucine": "Amino acid: Leucine",
    "lysine": "Amino acid: Lysine",
    "methionine": "Amino acid: Methionine",
    "phenylalanine": "Amino acid: Phenylalanine",
    "threonine": "Amino acid: Threonine",
    "tryptophan": "Amino acid: Tryptophan",
    "valine": "Amino acid: Valine",
    "starch": "Starch content in grams",
    "sugar": "Sugar content in grams",
    "omega_3_ala": "ALA Omega-3 fatty acid",
    "omega_3_eicosatrienoic_acid": "Omega-3: Eicosatrienoic acid",
    "omega_6_gamma_linoleic_acid": "Omega-6: Gamma-linolenic acid",
    "omega_6_dihomo_gamma_linoleic_acid": "Omega-6: Dihomo-gamma-linolenic acid",
    "omega_6_linoleic_acid": "Omega-6: Linoleic acid",
    "omega_6_arachidonic_acid": "Omega-6: Arachidonic acid",
    "omega_6_eicosadienoic_acid": "Omega-6: Eicosadienoic acid"
}

for col in numeric_cols:
    descriptions[col] = col.replace("_", " ").capitalize()

custom_types = {col: DataType.NUMBER if col in numeric_cols else DataType.TEXT for col in df.columns}

collection_name = "FoodNutrition4"
if client.collections.exists(collection_name):
    client.collections.delete(collection_name)

properties = []
for col in df.columns:
    prop = Property(
        name=col,
        data_type=custom_types[col],
        description=descriptions.get(col, col.replace("_", " ").capitalize())
    )
    properties.append(prop)

client.collections.create(
    name=collection_name,
    properties=properties,
    vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),
    generative_config=Configure.Generative.google(project_id=google_project_id)
)

collection = client.collections.get(collection_name)

with collection.batch.fixed_size(batch_size=100) as batch:
    for _, row in df.iterrows():
        batch.add_object(row.to_dict())
        if batch.number_errors > 10:
            print("Too many errors — stopping upload.")
            break

if collection.batch.failed_objects:
    print("Failed objects:", len(collection.batch.failed_objects))
else:
    print("Upload complete!")

client.close()
