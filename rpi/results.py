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

# DSL Query: groups by day
query = {
    "size": 0,  
    "query": {
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
                "high_temp": {
                    "percentiles": { "field": "Temperature" , "percents": [95]}
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
            "high_temp": b['high_temp']['values']['95.0']
        })
        df = pd.DataFrame(parsed_data)
        # Drop days where no temperature was recorded to avoid plotting nulls
        df = df.dropna(subset=['high_temp'])
        # Format the timestamp into a shorter, readable date string (YYYY-MM-DD)
        df['short_date'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')

    return df


def plot(df):
    plt.figure(figsize=(10, 6))
    plt.scatter(df['count_activate'], df['high_temp'], s=64, c=df.index, cmap='viridis')

    # color legend (time in days)
    cb=plt.colorbar()
    cticks = cb.get_ticks()
    cb.set_ticklabels(["Day {}".format(int(d-cticks[0])) for d in cticks])

    # labels data points by date
    for index, row in df.iterrows():
        plt.annotate(
            row['short_date'],                         # The text to display
            (row['count_activate'],row['high_temp']),   # The (x, y) point to label
            textcoords="offset points",                # How to position the text
            xytext=(5, 5),                             # Shift the text 5 points right and 5 points up
            ha='left',                                 # Horizontal alignment
            fontsize=6                                 # Keep font small to reduce clutter
        )
        
    plt.xlabel('Activations/day')
    plt.ylabel('Temperature 95th-p (°C)')
    plt.grid(True, alpha=0.3)
    plt.show()


if __name__ == '__main__':
    es_host=sys.argv[1]
    plot(get_data(f"http://{es_host}:9200/qrb_mon-alias/_search"))
