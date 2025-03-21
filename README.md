---
title: OCC2 MongoDB Report
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

XXX description du code python
## Loading the JSON into ElasticSearch


# Queries

### Easy queries

### Complex queries

### Hard Queries