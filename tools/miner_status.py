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
            r['message'] = "Hardware errors" # teraflux msg resp['STATUS'][0]['Msg'] is just "Summary"
            yield r


def main():
    parser = argparse.ArgumentParser(description='Tool to get error codes from miner APIs')
    parser.add_argument("--start_ip", required=True)
    parser.add_argument("--end_ip", required=True)
    parser.add_argument("--miner_type", choices=['whatsminer', 'teraflux', 'luxminer', "antminer"],
                        default='generic')
    parser.add_argument("--output", choices=['logstash', 'syslog'], default='logstash')
    args = parser.parse_args()

    my_logger = qrb_logging.get_logger("miner_status", args.output)

    for i in range(int(ipaddress.IPv4Address(args.start_ip)),
                   int(ipaddress.IPv4Address(args.end_ip))+1):
        ip = str(ipaddress.ip_address(i))
        try:
            if args.miner_type == "whatsminer":
                for stuff in whatsminer_get_error_codes(ip):
                    my_logger.error(stuff)
            elif args.miner_type == "teraflux" or args.miner_type == "luxminer" or args.miner_type == "antminer":
                for stuff in get_summary_hardware_errors(ip):
                    my_logger.error(stuff)
            # edevs is same or all except antminer
            if args.miner_type != "antminer":
                for stuff in miner_lib.edevs(ip):
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


if __name__ == "__main__":
    main()
