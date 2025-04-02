#!/usr/bin/python3

'''Tested with Whatsminer api_ver: 2.0.5

Usage: 

EXPORT PYTHONPATH=.
./miner_status.py --start_ip=10.0.1.27 --end_ip=10.0.1.100

'''

import argparse
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
    check_response(resp)
    print(resp)


def whatsminer_get_error_code(address, port=4028):
    """ 
    Get any current errors being reported by the miner.
    Yields tuples of strings of the form (date and time, error code, message)
    """
    sock = socket.socket()
    sock.connect((address, port))
    sock.send('{"cmd":"get_error_code"}'.encode())
    resp = json.loads(sock.recv(RECV_BUF_SIZE))
    whatsminer_codes.check_response(resp)
    for error in resp['Msg']['error_code']:
        # error is a dict with key=code, value=date and time
        for code in error:
            yield (
                error[code],  # timestamp
                code,         # integer  
                whatsminer_codes.WHATSMINER_ERROR_CODES.get(
                    int(code),
                    {"message": "{} not in dictionary".format(code)})
            )
    

def main():
    parser = argparse.ArgumentParser(description='Tool to get error codes from miner APIs')
    parser.add_argument("--start_ip", required=True)
    parser.add_argument("--end_ip", required=True)
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
                    # whatsminer_get_version(ip)
                    try:
                        for stuff in whatsminer_get_error_code(ip):
                            my_logger.error("miner_status: {} {}".format(ip, stuff))
                    except OSError as e:
                        my_logger.error("miner_status: {} {}".format(ip, e))


if __name__ == "__main__":
    main()

