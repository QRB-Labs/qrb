#!/usr/bin/python3
'''Results of Feedback control: reads temperature and pump
activations, grouped by day from elastic search, and does a scatter
plot.

'''

import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import sys

ES_HOST=sys.argv[1]
ES_URL = f"http://{ES_HOST}:9200/qrb_mon-alias/_search"
HEADERS = {"Content-Type": "application/json"}

# DSL Query: groups by day, filters for the host, and calculates both metrics
query = {
    "size": 0,  
    "query": {
        "term": { "host.hostname": "raspberrypi" }
    },
    "aggregations": {
        "daily_buckets": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": "1d"
            },
            "aggs": {
                "activate_count": {
                    "filter": { "term": { "message.keyword": "Activate" } }
                },
                "avg_temp": {
                    "avg": { "field": "Temperature" }
                }
            }
        }
    }

}

# Fetch Data via HTTP POST
response = requests.post(ES_URL, headers=HEADERS, data=json.dumps(query))
response.raise_for_status()
raw_data = response.json()

# Parse JSON into pandas data frame
buckets = raw_data['aggregations']['daily_buckets']['buckets']
parsed_data = []

for b in buckets:
    parsed_data.append({
        "timestamp": b['key_as_string'],
        "count_activate": b['activate_count']['doc_count'],
        "avg_temp": b['avg_temp']['value']
    })

df = pd.DataFrame(parsed_data)

# Drop days where no temperature was recorded to avoid plotting nulls
df = df.dropna(subset=['avg_temp'])

plt.figure(figsize=(10, 6))
plt.scatter(df['count_activate'], df['avg_temp'], alpha=0.6)

plt.xlabel('Water pump activations (min/day)')
plt.ylabel('Average temperature (°C)')
plt.grid(True, alpha=0.3)

plt.show()
