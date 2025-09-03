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
import json
from logstash import TCPLogstashHandler
from logstash.formatter import LogstashFormatterBase
import logging
import logging.handlers
import socket

import miner_api_codes
import miner_lib


def whatsminer_get_error_codes(address, port=4028):
    """
    Get any current errors being reported by the miner.
    Yields a dictionary
    """
    sock = socket.socket()
    sock.connect((address, port))
    sock.send('{"cmd":"get_error_code"}'.encode())
    resp = json.loads(sock.recv(miner_lib.RECV_BUF_SIZE))
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


def teraflux_get_error_codes(address, port=4028):
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


def edevs(address, port=4028):
    """
    Get temperature of miner
    Yields a dictionary
    """
    sock = socket.socket()
    sock.connect((address, port))
    sock.send('{"command":"edevs"}'.encode())
    recv_bytes = b''
    while True:
        chunk = sock.recv(miner_lib.RECV_BUF_SIZE)
        if not chunk:
            break
        recv_bytes += chunk
    assert len(recv_bytes) < miner_lib.RECV_BUF_SIZE
    resp = json.loads(recv_bytes)
    miner_lib.check_response(resp)

    for r in resp['DEVS']:
        r['ip_address'] = address
        r['datetime'] = datetime.fromtimestamp(resp['STATUS'][0].get('When', datetime.now().timestamp()))
        r['code'] = resp['STATUS'][0].get('Code', 9)
        r['message'] = resp['STATUS'][0]['Msg']
        if r.get('Enabled') == 'Y':
            r['Enabled'] = True  # whatsminer returns 'Y'/'N' instead of boolean
        if r.get('Enabled') == 'N':
            r['Enabled'] = False
        yield r


class LogstashFormatter(LogstashFormatterBase):
    def format(self, record):
        message = record.msg
        if 'datetime' in message:
            message['@timestamp'] = message['datetime'].strftime('%Y-%m-%dT%H:%M:%S.%f')
            del message['datetime']

        message.update({
            'host': {'ip': record.msg['ip_address']},
            'path': record.pathname,
            'tags': self.tags,
            'type': self.message_type,
            'level': record.levelname,
            'logger_name': record.name,
        })
        del message['ip_address']
        return self.serialize(message)


def main():
    parser = argparse.ArgumentParser(description='Tool to get error codes from miner APIs')
    parser.add_argument("--start_ip", required=True)
    parser.add_argument("--end_ip", required=True)
    parser.add_argument("--miner_type", choices=['whatsminer', 'teraflux'],
                        default='whatsminer')
    parser.add_argument("--output", choices=['logstash', 'syslog'], default='logstash')
    args = parser.parse_args()

    start_ip_octets = args.start_ip.split('.')
    end_ip_octets = args.end_ip.split('.')
    assert len(start_ip_octets) == 4
    assert len(end_ip_octets) == 4

    my_logger = logging.getLogger("miner_status")
    my_logger.setLevel(logging.DEBUG)

    if args.output == 'syslog':
        my_logger.addHandler(logging.handlers.SysLogHandler('/dev/log'))
    if args.output == 'logstash':
        handler = TCPLogstashHandler(host='192.168.6.100', port=5959)
        handler.setFormatter(LogstashFormatter())
        my_logger.addHandler(handler)

    for octet0 in range(int(start_ip_octets[0]), int(end_ip_octets[0])+1):
        for octet1 in range(int(start_ip_octets[1]), int(end_ip_octets[1])+1):
            for octet2 in range(int(start_ip_octets[2]), int(end_ip_octets[2])+1):
                for octet3 in range(int(start_ip_octets[3]), int(end_ip_octets[3])+1):
                    ip = '.'.join(map(str, [octet0, octet1, octet2, octet3]))
                    try:
                        if args.miner_type == "whatsminer":
                            for stuff in whatsminer_get_error_codes(ip):
                                my_logger.error(stuff)
                        elif args.miner_type == "teraflux":
                            for stuff in teraflux_get_error_codes(ip):
                                my_logger.error(stuff)
                        # edevs is cgminer same or both
                        for stuff in edevs(ip):
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
                        stuff['code'] = stuff['Code']
                        stuff['message'] = stuff['Msg']
                        stuff['datetime'] = datetime.fromtimestamp(stuff['When'])
                        my_logger.error(stuff)


if __name__ == "__main__":
    main()
