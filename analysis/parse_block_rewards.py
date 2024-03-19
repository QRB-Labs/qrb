'''Extract block-rewards.csv from 
https://bitcoinvisuals.com/static/data/data_daily.csv
'''
import pandas as pd
import datetime as dt

daily_data = pd.read_csv("block_rewards.csv")
daily_data['DateTime']=pd.to_datetime(daily_data['day'])
daily_data.set_index('DateTime', inplace=True)
daily_data.rename(columns={'blockreward_median': 'BTC'}, inplace=True)
daily_data['BTC'].to_csv('block-rewards.csv')


