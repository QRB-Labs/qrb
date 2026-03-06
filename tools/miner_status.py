#!/usr/bin/python3

'''Query miner API for status and log results to syslgog or logstash.

Output log record format is

miner_status: {'ip_address': <ip>, 'datetime': <datetime>, 'code': <int code>, <key>: <value>, ...}

Usage:

EXPORT PYTHONPATH=.
./miner_status.py --start_ip=10.0.1.27 --end_ip=10.0.1.100

Tested with
- Whatsminer api version 2.0.5
- Teraflux api version 1.0
'''

import argparse
from datetime import datetime
import ipaddress
import json
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from mdb import get_data
import miner_api_codes
import miner_lib
import qrb_logging


def whatsminer_get_error_codes(address, port=4028):
    """
    Get any current errors being reported by the miner.
    Yields a dictionary
    """
    resp = miner_lib.send_json('{"cmd":"get_error_code"}', address, port)
    miner_lib.check_response(resp)
    for error in resp['Msg']['error_code']:
        # error is a dict with key=code, value=date and time
        for code in error:
            r = miner_api_codes.WHATSMINER_ERROR_CODES.get(
                int(code),
                {"message": "{} not in dictionary".format(code)})
            r['ip_address'] = address
            if error[code]:
                r['datetime'] = datetime.strptime(error[code], '%Y-%m-%d %H:%M:%S')
            r['code'] = int(code)
            yield r


def get_summary_hardware_errors(address, port=4028):
    """
    Get summary of miner status for any miner where there is 'Harware Errors'
    Yields a dictionary
    """
    resp = miner_lib.get_summary(address, port)
    miner_lib.check_response(resp)
    for r in resp['SUMMARY']:
        if r['Hardware Errors'] > 0:
            r['ip_address'] = address
            r['datetime'] = datetime.fromtimestamp(resp['STATUS'][0]['When'])
            r['code'] = resp['STATUS'][0]['Code']
            if resp['STATUS'][0]['Msg'] == "Summary":
                r['message'] = "{} hardware errors".format(r['Hardware Errors'])
            else:
                r['message'] = resp['STATUS'][0]['Msg']
            yield r


def ip_range(start_ip, end_ip):
    for ip in range(int(ipaddress.IPv4Address(start_ip)),
                    int(ipaddress.IPv4Address(end_ip))+1):
        yield str(ipaddress.ip_address(ip))


def ips_from_sheets(key_file, sheet_url, worksheets):
    for fname in get_data.sync_sheets(key_file, sheet_url, worksheets):
        df = pd.read_csv(fname)
        for ip in df['ip_address'].dropna():
            yield(ip)


def main():
    parser = argparse.ArgumentParser(description='Tool to get error codes from miner APIs')
    parser.add_argument("--start_ip")
    parser.add_argument("--end_ip")
    parser.add_argument("--miner_type", choices=['whatsminer', 'teraflux', 'luxminer', 'antminer', 'generic'],
                        default=None)
    parser.add_argument('--sheet_url', type=str, help="Google spreadsheet url", default=None)
    parser.add_argument('--worksheets', nargs='+',
                        help='list of worksheet names eg --worksheets "Miners" "Other miners"',  default=None)

    parser.add_argument("--output", choices=['logstash', 'syslog'], default='logstash')
    parser.add_argument('--key_file', type=str, default="/home/nemo/gcloud/qrb-labs-mdb.json")
    args = parser.parse_args()


    ip_range_mode = bool(args.start_ip and args.end_ip)
    sheets_mode = bool(args.sheet_url and args.worksheets)

    assert (ip_range_mode and not sheets_mode) or (not ip_range_mode and sheets_mode), \
        "Input option must be either start_ip and end_ip, or sheet_url and worksheets"

    my_logger = qrb_logging.get_logger("miner_status", args.output)
    my_logger.debug({'message': "miner_status starting..."})

    if ip_range_mode:
        ip_generator = ip_range(args.start_ip, args.end_ip)

    if sheets_mode:
        ip_generator = ips_from_sheets(args.key_file, args.sheet_url, args.worksheets)

    for ip in ip_generator:
        try:
            if args.miner_type:
                miner_type = args.miner_type
            else:
                miner_type = miner_lib.guess_miner_type(ip)
                my_logger.debug({'ip_address': ip,'message': f"Guessed miner_type = {miner_type}"})

            base_msg = {}
            # basic hardware info like mac address and serial numbers
            if miner_type == "whatsminer":
                base_msg.update(miner_lib.whatsminer_get_miner_info(ip))
            if miner_type == "teraflux":
                base_msg.update(miner_lib.teraflux_get_miner_info(ip))
            # pool URL and username
            for stuff in miner_lib.get_pools(ip):
                stuff.update(base_msg)
                my_logger.error(stuff)

            # device monitoring
            if miner_type != "antminer":
                for stuff in miner_lib.edevs(ip):
                    my_logger.error(stuff)

            # errors
            if miner_type == "whatsminer":
                for stuff in whatsminer_get_error_codes(ip):
                    my_logger.error(stuff)
            elif miner_type == "teraflux" or miner_type == "luxminer" or miner_type == "antminer":
                for stuff in get_summary_hardware_errors(ip):
                    my_logger.error(stuff)

        except OSError as e:
            stuff = {
                'ip_address': ip,
                'message': '{}'.format(e),
                'code': -e.errno
            }
            my_logger.error(stuff)
        except json.decoder.JSONDecodeError as e:
            my_logger.debug({
                'ip_address': ip,
                'message': '{}'.format(e),
                'code': -1
            })
        except miner_lib.MinerAPIError as e:
            stuff = e.resp
            stuff['ip_address'] = ip
            my_logger.error(stuff)
        except TypeError as e:
            my_logger.debug({
                'ip_address': ip,
                'message': '{}'.format(e),
                'code': -2
            })


if __name__ == "__main__":
    main()
