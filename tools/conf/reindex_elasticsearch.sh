#!/bin/bash

curl --user elastic:$ELASTIC_PASSWORD  -X PUT http://localhost:9200/_reindex -H "Content-Type: application/json" -d'
{
  "source": {
    "index": "qrb_mon"
  },
  "dest": {
    "index": "qrb_mon_dedup"
  }
  "script": {
    "lang": "painless",
    "source": "ctx._id = ctx.@timestamp +  '_' +  ctx.host.ip + '_' + ctx.code + '_' + ctx.message"
  }
}
'
