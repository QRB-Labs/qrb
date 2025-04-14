#!/bin/bash

curl --user elastic:$ELASTIC_PASSWORD  -X PUT http://localhost:9200/_security/role/logstash_writer -H "Content-Type: application/json" -d'
{

  "cluster":  ["monitor", "manage", "all"],
  "indices": [
    {
      "names": ["qrb_mon", "qrb_mon-*"],
      "privileges": ["write", "create", "index", "auto_configure","create_index","manage","all"]
    }
  ],
  "description": "Role for Logstash to write to qrb_mon index"
}
'

curl --user elastic:$ELASTIC_PASSWORD -X POST "localhost:9200/_security/user/logstash_writer?pretty" -H 'Content-Type: application/json' -d'
{
  "password" : "sumdumting",
  "roles" : [ "logstash_writer" ],
}
'

curl --user elastic:$ELASTIC_PASSWORD -X POST "localhost:9200/_security/role_mapping/mapping1?pretty" -H 'Content-Type: application/json' -d'
{
  "roles": [ "logstash_writer"],
  "enabled": true,
  "rules": {
    "field" : { "username" : "logstash_writer" }
  },
  "metadata" : {
    "version" : 1
  }
}
'

curl --user elastic:$ELASTIC_PASSWORD  -X PUT http://localhost:9200/_security/role/anonymous_search -H "Content-Type: application/json" -d'
{
  "cluster": ["monitor"],
  "indices": [
    {
      "names": ["qrb_mon", "qrb_mon-*"],
      "privileges": ["read"]
    }
  ]
}
'

curl --user elastic:$ELASTIC_PASSWORD -X POST "localhost:9200/_security/role_mapping/mapping2?pretty" -H 'Content-Type: application/json' -d'
{
  "roles": [ "anonymous_search"],
  "enabled": true,
  "rules": {
    "field" : { "username" : "*"}
  },
  "metadata" : {
    "version" : 1
  }
}
'
