---
title: OCC2 Elasticsearch Report
author:
 - Klink, Carl
 - Lefebvre, Romain
 - Matthews, Louis-Marie
 - Muller, Julie
date: March the 21th, 2025
---

# Setup

## Cloning the repository

We start by cloning our repository, which contains the original version of the dataset we are working on: `earthquakes_big.geojson.json`.

```
git clone https://github.com/Jlemlr/Elasticsearch
```

## Preparing the dataset

First, as instructed, we will display one row of the original dataset. (We only formatted the first row for readability, no transformation of any kind was performed.)

```json
{
"type": "Feature",
"properties": {
	"mag": 0.8,
	"place": "6km W of Cobb, California",
	"time": 1370259968000,
	"updated": 1370260630761,
	"tz": -420,
	"url": "http://earthquake.usgs.gov/earthquakes/eventpage/nc72001620",
	"detail": "http://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/
	  nc72001620.geojson",
	"felt": null,
	"cdi": null,
	"mmi": null,
	"alert": null,
	"status": "AUTOMATIC",
	"tsunami": null,
	"sig": 10,
	"net": "nc",
	"code": "72001620",
	"ids": ",nc72001620,",
	"sources": ",nc,",
	"types": ",general-link,geoserve,nearby-cities,origin,phase-data,
	scitech-link,",
	"nst": null,
	"dmin": 0.00898315,
	"rms": 0.06,
	"gap": 82.8,
	"magType": "Md",
	"type": "earthquake"
},
"geometry": {
	"type": "Point",
	"coordinates": [
		-122.7955,
		38.8232,
		3
	]
},
"id": "nc72001620"
}
```

We will also make sure to keep a note of the number of lines of the original dataset.

```bash
root@6d7fb3f3b522:/workspaces/MongoDB# wc -l earthquakes_big.geojson.json 
7668 earthquakes_big.geojson.json
```

There are are 7668 newline characters. In other words, there are 766**9** lines. :) 
We now run `utils.py` as we did for `MangoDB`, it outputs `earthquakes_big.geojson.json`.

## Adapting the dataset to Elasticsearch using `Elastic_format.py`

Here is a breakup of this python code :

1. **Load JSON into a DataFrame**
- The script reads a newline-delimited JSON file containing earthquake data using `pd.read_json(input_file, lines=True)`.
- This loads each JSON object (earthquake record) as a row in a pandas DataFrame.

2. **Define a Processing Function**
- `process_feature(row)` takes a row from the DataFrame and extracts relevant fields.
- It creates an Elasticsearch bulk API metadata entry using the earthquake's `id`.
- It then constructs the document with key earthquake properties (e.g., magnitude, location, time, depth).
- The coordinates from GeoJSON format are transformed into Elasticsearch’s `geo_point` format (`lat`, `lon`).

3. **Apply Processing to All Rows**
- The function is applied to each row using `df.apply(process_feature, axis=1)`, generating a list of bulk API entries.

4. **Format Data for Elasticsearch**
- The metadata and document pairs are flattened into a single list, ensuring each entry is newline-separated.
- The formatted data is written to `earthquakes_bulk.json`, making it ready for Elasticsearch !

## Loading the JSON into ElasticSearch

Pull and run the container 
```
docker pull nshou/elasticsearch-kibana:latest
docker run -d -p 9200:9200 -p 5601:5601 --name elasticsearch nshou/elasticsearch-kibana
```

Get the login infos to access elasticsearch app
``` 
docker logs -f elasticsearch
```
There it gives you the login info and you can access https://localhost:5601/ (the port might be different check the output of the query)

Once on the elastic search webapp, click on import data and import the `earthquakes_bulk.json` file and set `earthquake` as index.
Then to execute queries go to `Dev tools`.

# Queries

## Simple Queries

1. **Earthquakes in California with Magnitude > 3 and Status "AUTOMATIC"**

```
{
  "_source": ["mag","place","status"],
  "query": {
    "bool": {
      "must": [
        { "match": { "place": "California" } },
        { "range": { "mag": { "gt": 3 } } },
        { "match": { "status": "AUTOMATIC" } }
      ]
    }
  }
}
```

2. **Earthquakes Where the Updated Time Exceeds the Event Time by at Least 5 Minutes**

Note: The time field is in epoch milliseconds while updated is also stored in epoch milliseconds.

```
{
  "_source": ["mag","place","time"],
  "query": {
    "script": {
      "script": {
        "source": """
          if (doc['updated'].size()==0 || doc['time'].size()==0) {
            return false;
          } else {
            long updatedMillis = doc['updated'].value.toInstant().toEpochMilli();
            long timeMillis = doc['time'].value.toInstant().toEpochMilli();
            return updatedMillis - timeMillis >= 300000;
          }
        """,
        "lang": "painless"
      }
    }
  }
}

```

3. **Earthquakes with a Gap Greater Than 100**

Assuming a higher gap may indicate less reliable phase picks

```
{
  "_source": ["mag","place","gap"],
  "query": {
    "range": {
      "gap": {
        "gt": 100
      }
    }
  }
}
```

4. Earthquakes with a Non-Zero Tsunami Warning
(If a tsunami warning was issued, the field should be 1 instead of null or 0)

```
{
  "_source": ["mag","place","tsunami"],
  "query": {
    "term": {
      "tsunami": 1
    }
  }
}
```

5. **Earthquakes Within a Specific Geographic Bounding Box**

This example looks for events in a region near California. Adjust the bounding box coordinates as needed.

```
{
  "_source": ["mag","place","location"],
  "query": {
    "script": {
      "script": {
        "source": """
          if (doc['location.lat'].size() > 0 && doc['location.lon'].size() > 0) {
            double lat = doc['location.lat'].value;
            double lon = doc['location.lon'].value;
            return lat <= params.top && lat >= params.bottom && lon >= params.left && lon <= params.right;
          }
          return false;
        """,
        "lang": "painless",
        "params": {
          "top": 39.0,
          "bottom": 38.0,
          "left": -123.0,
          "right": -122.0
        }
      }
    }
  }
}
```

6. **Earthquakes with a Very Close Station Distance (`dmin < 0.01`)**

Lower dmin values can indicate that the station was very near the epicenter

```
{
  "_source": ["mag","place","range"],
  "query": {
    "range": {
      "dmin": {
        "lt": 0.01
      }
    }
  }
}
```

## Complex Queries

7. **Daily Statistics: Count and Average Magnitude Per Day**

Aggregates events by day using a date histogram on the time field and computes the average magnitude

```
{
  "size": 0,
  "aggs": {
    "earthquakes_per_day": {
      "date_histogram": {
        "field": "time",
        "calendar_interval": "day"
      },
      "aggs": {
        "avg_magnitude": {
          "avg": { "field": "mag" }
        }
      }
    }
  }
}
```

8. **Average Magnitude and Depth per Year**

```
GET earthquakes/_search
{
  "size": 0,
  "aggs": {
    "years": {
      "date_histogram": {
        "field": "time",
        "calendar_interval": "year"
      },
      "aggs": {
        "avg_magnitude": {
          "avg": {
            "field": "mag"
          }
        },
        "avg_depth": {
          "avg": {
            "field": "depth"
          }
        }
      }
    }
  }
}
```

## Hard Queries

9. **Closest Earthquake (with Magnitude > 4.0 and in the Last 7 Days) to a Given Location**

This query sorts by geographic distance using `geo_point` (using only the first two values: longitude and latitude).
For the time filter, since we have a date field with `epoch_millis`, `now - 7d` works directly.

```
PUT /earthquakes_v2
{
  "mappings": {
    "properties": {
      "location": {
        "type": "geo_point"
      },
      "mag": { "type": "double" },
      "place": { "type": "text" },
      "time": { "type": "date" },
      "updated": { "type": "date" },
      "tz": { "type": "long" },
      "url": { "type": "keyword" },
      "detail": { "type": "keyword" },
      "status": { "type": "keyword" },
      "sig": { "type": "long" },
      "net": { "type": "keyword" },
      "code": { "type": "keyword" },
      "ids": { "type": "keyword" },
      "sources": { "type": "keyword" },
      "types": { "type": "keyword" },
      "nst": { "type": "long" },
      "dmin": { "type": "double" },
      "rms": { "type": "double" },
      "gap": { "type": "double" },
      "magType": { "type": "keyword" },
      "event_type": { "type": "keyword" },
      "felt": { "type": "long" },
      "cdi": { "type": "double" },
      "mmi": { "type": "double" },
      "alert": { "type": "keyword" },
      "tsunami": { "type": "long" },
      "depth": { "type": "double" }
    }
  }
}

POST /_reindex
{
  "source": {
    "index": "earthquakes"
  },
  "dest": {
    "index": "earthquakes_v2"
  }
}

GET earthquakes_v2/_search
{
  "size": 10,
  "_source": ["mag","place","time"],
  "query": {
    "match_all": {}
  },
  "sort": [
    {
      "_geo_distance": {
        "location": {
          "lat": 37.7749,
          "lon": -122.4194
        },
        "order": "asc",
        "unit": "km"
      }
    }
  ]
}
```
