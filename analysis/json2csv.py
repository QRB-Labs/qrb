'''Convert JSON files from blockchain.com to CSV'''
import sys
import json
from datetime import datetime, timezone


data = json.load(open(sys.argv[1]))
metric = data['metric1']
print('Timestamp,{}'.format(metric))
for row in data[metric]:
    x = row['x']/1000   # ms to s timestamp
    t = datetime.fromtimestamp(x).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print("{},{}".format(t, row['y']))
