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

HEADERS = {"Content-Type": "application/json"}

# DSL Query: groups by day, filters for the host, and calculates both metrics
query = {
    "size": 0,  
    "query": {
#        "term": { "logger_name": "rpi.feedback_control"}
        "bool": {
            "filter": [
                { "term": { "logger_name": "rpi.feedback_control" } },
                { "range": { "@timestamp": { "gte": "now-90d/d" } } }
            ]
        }
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


def get_data(es_url):
    # Fetch Data via HTTP POST
    response = requests.post(es_url, headers=HEADERS, data=json.dumps(query))
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
        # Format the timestamp into a shorter, readable date string (YYYY-MM-DD)
        df['short_date'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')

    return df


def plot(df):
    plt.figure(figsize=(10, 6))
    plt.scatter(df['avg_temp'], df['count_activate'], s=10, c=df.index, cmap='viridis')
    cb=plt.colorbar()
    cticks = cb.get_ticks()
    cb.set_ticklabels(["Day {}".format(int(d-cticks[0])) for d in cticks])

    # Add labels to the data points ---
    for index, row in df.iterrows():
        plt.annotate(
            row['short_date'],                         # The text to display
            (row['avg_temp'], row['count_activate']),  # The (x, y) point to label
            textcoords="offset points",                # How to position the text
            xytext=(5, 5),                             # Shift the text 5 points right and 5 points up
            ha='left',                                 # Horizontal alignment
            fontsize=6                                 # Keep font small to reduce clutter
        )

    plt.ylabel('Activations/day)')
    plt.xlabel('Average temperature (°C)')
    plt.grid(True, alpha=0.3)
    plt.show()


if __name__ == '__main__':
    es_host=sys.argv[1]
    plot(get_data(f"http://{es_host}:9200/qrb_mon-alias/_search"))
