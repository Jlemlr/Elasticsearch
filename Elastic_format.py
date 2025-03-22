import json
import pandas as pd

# Load the original GeoJSON file into a pandas DataFrame
input_file = "earthquakes_big.geojson.json"  # Update with the path to your file
output_file = "earthquakes_bulk.json"  # The output file in Elasticsearch Bulk format

# Read JSONL file directly into a DataFrame
df = pd.read_json(input_file, lines=True)

# Function to process each feature
def process_feature(row):
    earthquake_id = row["id"]
    metadata = {"index": {"_index": "earthquakes", "_id": earthquake_id}}
    
    properties = row["properties"]
    geometry = row["geometry"]
    
    doc = {
        "mag": properties.get("mag"),
        "place": properties.get("place"),
        "time": properties.get("time"),
        "updated": properties.get("updated"),
        "tz": properties.get("tz"),
        "url": properties.get("url"),
        "detail": properties.get("detail"),
        "felt": properties.get("felt"),
        "cdi": properties.get("cdi"),
        "mmi": properties.get("mmi"),
        "alert": properties.get("alert"),
        "status": properties.get("status"),
        "tsunami": properties.get("tsunami"),
        "sig": properties.get("sig"),
        "net": properties.get("net"),
        "code": properties.get("code"),
        "ids": properties.get("ids"),
        "sources": properties.get("sources"),
        "types": properties.get("types"),
        "nst": properties.get("nst"),
        "dmin": properties.get("dmin"),
        "rms": properties.get("rms"),
        "gap": properties.get("gap"),
        "magType": properties.get("magType"),
        "event_type": properties.get("type"),  # Rename "type" to "event_type"
        "location": {
            "lat": geometry["coordinates"][1],
            "lon": geometry["coordinates"][0]
        },
        "depth": geometry["coordinates"][2]
    }
    
    return json.dumps(metadata), json.dumps(doc)

# Apply function to process all rows
df["bulk_data"] = df.apply(process_feature, axis=1)

# Flatten and save to file
bulk_data = [item for sublist in df["bulk_data"].tolist() for item in sublist]

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(bulk_data) + "\n")  # Ensure newline-separated JSON

print(f"Successfully formatted data! Saved as {output_file}")