#!/bin/bash
#
# Download data series from blockchain.com into CSVs

export DATA_SERIES=("avg-block-size" "estimated-transaction-volume" "hash-rate" "block-rewards"  "miners-revenue" "n-transactions" "transaction-fees" "transaction-fees-usd")

for d in "${DATA_SERIES[@]}"; do

    echo $d
    (echo "Timestamp,$d" ; wget "https://api.blockchain.info/charts/$d?timespan=all&rollingAverage=24hours&sampled=false&format=csv" -O  - ) > $d.csv
done


# These series are very large so sampled=true
export DATA_SERIES=("market-cap" "mempool-size")

for d in "${DATA_SERIES[@]}"; do

    echo $d
    (echo "Timestamp,$d" ; wget "https://api.blockchain.info/charts/$d?timespan=all&rollingAverage=24hours&sampled=true&format=csv" -O  - ) > $d.csv
done

# Download data and create block-rewards.csv

wget https://bitcoinvisuals.com/static/data/data_daily.csv -O block_rewards.csv
python3 parse_block_rewards.py
