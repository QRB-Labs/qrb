#!/bin/bash

# Script to convert old qrb_mon index (which didn't deduplicate repeated status from miner api to new one which does.
# The filter in logstash.conf ensures new docs have an equivalent unique constraint

curl --user elastic:$ELASTIC_PASSWORD  -X PUT http://localhost:9200/_reindex -H "Content-Type: application/json" -d'
{
  "source": {
    "index": "qrb_mon"
  },
  "dest": {
    "index": "qrb_mon-dedup2"
  },
  "script": {
    "lang": "painless",
    "source": "if(ctx._source.host != null && ctx._source.message != null) {ctx._id = ctx._source.timestamp + ctx._source.host.ip + ctx._source.code + ctx._source.message.sha256();} if(ctx._source.Slot != null) {ctx._id = ctx._id + ctx._source.Slot;}"
  }
}
'
