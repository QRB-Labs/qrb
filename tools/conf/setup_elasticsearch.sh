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
  "roles": [ "anonymous_search", "kibana_user"],
  "enabled": true,
  "rules": {
    "field" : { "username" : "*"}
  },
  "metadata" : {
    "version" : 1
  }
}
'


curl -u elastic:$ELASTIC_PASSWORD -X PUT "http://localhost:9200/qrb_mon-000001?pretty" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "index.number_of_shards": 1,
    "index.number_of_replicas": 0
  }
}'


 curl -u elastic:$ELASTIC_PASSWORD -X PUT "http://localhost:9200/_ilm/policy/qrb_policy" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_primary_shard_size": "10gb",
            "max_age": "7d"
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'


curl -u elastic:$ELASTIC_PASSWORD -X PUT "http://localhost:9200/qrb_mon-000001/_settings" -H 'Content-Type: application/json' -d'
{
  "index.lifecycle.name": "qrb_policy",
  "index.lifecycle.rollover_alias": "qrb_mon-alias"
}'


curl -u elastic:$ELASTIC_PASSWORD -X PUT "http://localhost:9200/_index_template/qrb_mon_template" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["qrb_mon-*"],
  "template": {
    "settings": {
      "index.lifecycle.name": "qrb_policy",
      "index.lifecycle.rollover_alias": "qrb_mon-alias",
      "index.number_of_shards": 1,
      "index.number_of_replicas": 0
    }
  }
}'

curl -u elastic:$ELASTIC_PASSWORD -X PUT "http://localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "persistent": {
    "indices.breaker.fielddata.limit": "40%",
    "indices.breaker.request.limit": "30%",
    "indices.breaker.total.limit": "70%"
  }
}'
