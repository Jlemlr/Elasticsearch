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

8. Average Magnitude and Depth per Year

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









