#!/usr/bin/python3

'''Query miner API for status and log results to syslgog.

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
import json
import socket
import logging
import logging.handlers

import whatsminer_codes


RECV_BUF_SIZE=4096


def whatsminer_get_version(address, port=4028):
    sock = socket.socket()
    sock.connect((address, port))
    sock.send('{"cmd":"get_version"}'.encode())
    resp = json.loads(sock.recv(RECV_BUF_SIZE))
    return resp


def teraflux_get_version(address, port=4028):
    sock = socket.socket()
    sock.connect((address, port))
    sock.send('{"command":"version"}'.encode())
    resp = json.loads(sock.recv(RECV_BUF_SIZE))
    print(resp)


def whatsminer_get_error_code(address, port=4028):
    """
    Get any current errors being reported by the miner.
    Yields a dictionary
    """
    sock = socket.socket()
    sock.connect((address, port))
    sock.send('{"cmd":"get_error_code"}'.encode())
    resp = json.loads(sock.recv(RECV_BUF_SIZE))
    whatsminer_codes.check_response(resp)

    for error in resp['Msg']['error_code']:
        # error is a dict with key=code, value=date and time
        for code in error:
            r= whatsminer_codes.WHATSMINER_ERROR_CODES.get(
                int(code),
                {"message": "{} not in dictionary".format(code)})
            r['ip_address'] = address
            r['datetime'] = error[code]
            r['code'] = int(code)
            yield r


def teraflux_summary(address, port=4028):
    """
    Get summary of miner status for any miner where there is 'Harware Errors'
    Yields a dictionary
    """
    sock = socket.socket()
    sock.connect((address, port))
    sock.send('{"command":"summary"}'.encode())
    resp = json.loads(sock.recv(RECV_BUF_SIZE))
    whatsminer_codes.check_response(resp['STATUS'][0])

    for r in resp['SUMMARY']:
        if r['Hardware Errors'] > 0:
            r['ip_address'] = address
            r['datetime'] = '{}'.format(datetime.fromtimestamp(resp['STATUS'][0]['When']))
            r['code'] = resp['STATUS'][0]['Code']
            yield r


def main():
    parser = argparse.ArgumentParser(description='Tool to get error codes from miner APIs')
    parser.add_argument("--start_ip", required=True)
    parser.add_argument("--end_ip", required=True)
    parser.add_argument("--miner_type", choices=['whatsminer', 'teraflux'],
                        default='whatsminer')
    args = parser.parse_args()

    start_ip_octets = args.start_ip.split('.')
    end_ip_octets = args.end_ip.split('.')
    assert len(start_ip_octets) == 4
    assert len(end_ip_octets) == 4

    my_logger = logging.getLogger("miner_status")
    my_logger.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler('/dev/log')
    my_logger.addHandler(handler)

    for octet0 in range(int(start_ip_octets[0]), int(end_ip_octets[0])+1):
        for octet1 in range(int(start_ip_octets[1]), int(end_ip_octets[1])+1):
            for octet2 in range(int(start_ip_octets[2]), int(end_ip_octets[2])+1):
                for octet3 in range(int(start_ip_octets[3]), int(end_ip_octets[3])+1):
                    ip = '.'.join(map(str, [octet0, octet1, octet2, octet3]))
                    try:
                        if args.miner_type == "whatsminer":
                            func = whatsminer_get_error_code
                        elif args.miner_type == "teraflux":
                            func = teraflux_get_error_code
                            teraflux_get_version(ip)
                        for stuff in func(ip):
                            my_logger.error("miner_status: {}".format(stuff))
                    except OSError as e:
                        stuff = {
                            'ip_address': ip,
                            'message:': '{}'.format(e)
                        }
                        my_logger.error("miner_status: {}".format(stuff))


if __name__ == "__main__":
    main()
