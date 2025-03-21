# Simple Queries
1. Earthquakes in California with Magnitude > 3 and Status "AUTOMATIC"


```
{
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

2. Earthquakes Where the Updated Time Exceeds the Event Time by at Least 5 Minutes
Note: The time field is in epoch milliseconds while updated is also stored in epoch milliseconds.

```
{
  "query": {
    "script": {
      "script": {
        "source": "doc['updated'].value - doc['time'].value >= 300000", 
        "lang": "painless"
      }
    }
  }
}
```

3. Earthquakes with a Gap Greater Than 100
(Assuming a higher gap may indicate less reliable phase picks)

```
{
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
  "query": {
    "term": {
      "tsunami": 1
    }
  }
}
```

5. Earthquakes Within a Specific Geographic Bounding Box
(This example looks for events in a region near California. Adjust the bounding box coordinates as needed.)

```
{
  "query": {
    "bool": {
      "filter": {
        "geo_bounding_box": {
          "coordinates": {
            "top_left": { "lat": 39.0, "lon": -123.0 },
            "bottom_right": { "lat": 38.0, "lon": -122.0 }
          }
        }
      }
    }
  }
}
```

6. Earthquakes with a Very Close Station Distance (dmin < 0.01)
(Lower dmin values can indicate that the station was very near the epicenter)

```
{
  "query": {
    "range": {
      "dmin": {
        "lt": 0.01
      }
    }
  }
}
```

# Complex Queries

7. Daily Statistics: Count and Average Magnitude Per Day
(Aggregates events by day using a date histogram on the time field and computes the average magnitude)

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

8. Top 5 Places by Number of Earthquakes with Their Average Magnitude
Using the place.keyword field to aggregate by place.

```
{
  "size": 0,
  "aggs": {
    "top_places": {
      "terms": {
        "field": "place.keyword",
        "size": 5
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

9. Closest Earthquake (with Magnitude > 4.0 and in the Last 7 Days) to a Given Location

This query sorts by geographic distance. It assumes your coordinates field is mapped as a geo_point (using only the first two values: longitude and latitude).
For the time filter, if your time field is a date field with epoch_millis, "now-7d" works directly. If not, convert "now-7d" to the corresponding epoch millisecond value.

```
{
  "size": 1,
  "sort": [
    {
      "_geo_distance": {
        "coordinates": {
          "lat": 38.87,
          "lon": -122.8
        },
        "order": "asc",
        "unit": "km",
        "mode": "min",
        "distance_type": "arc"
      }
    }
  ],
  "query": {
    "bool": {
      "must": [
        { "range": { "mag": { "gt": 4 } } },
        { "range": { "time": { "gte": "now-7d" } } }
      ]
    }
  }
}
```









