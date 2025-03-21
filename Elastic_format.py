import json

# Load the original GeoJSON file
input_file = "earthquakes_big.geojson.json"   # Update with the path to your file
output_file = "earthquakes_bulk.json"  # The output file in Elasticsearch Bulk format

# Open input and output files
with open(input_file, "r", encoding="utf-8") as f:
    # Read each line and parse as a separate JSON object
    lines = f.readlines()

bulk_data = []  # List to store the fixed JSON lines

# Iterate over each line in the file
for line in lines:
    feature = json.loads(line.strip())  # Parse each JSON object
    earthquake_id = feature["id"]
    
    # Create the Elasticsearch Bulk API metadata line
    metadata = {"index": {"_index": "earthquakes", "_id": earthquake_id}}
    bulk_data.append(json.dumps(metadata))  # Convert to JSON string

    # Extract relevant fields
    properties = feature["properties"]
    geometry = feature["geometry"]
    
    # Convert GeoJSON coordinates to Elasticsearch geo_point format
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
            "lat": geometry["coordinates"][1],  # Latitude
            "lon": geometry["coordinates"][0]   # Longitude
        },
        "depth": geometry["coordinates"][2]  # Depth in km
    }

    bulk_data.append(json.dumps(doc))  # Convert to JSON string

# Write the processed data to a new file
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(bulk_data) + "\n")  # Ensure newline-separated JSON

print(f"✅ Successfully formatted data! Saved as {output_file}")