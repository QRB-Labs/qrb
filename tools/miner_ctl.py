#!/usr/bin/python3


import argparse
import json
import logging
import socket
import time

from hashlib import sha256
from base64 import b64encode

RECV_BUF_SIZE=4096


def get_token(address, port=4028):
    '''
    Get data needed to construct a token for writeable API.
    
    @returns a dict like {'STATUS': 'S',
                          'When': 1754491136,
                          'Code': 134,
                          'Msg': {'time': '1136', 'salt': 'BQ5hoXV9', 'newsalt': '9tfYlMf9'},
                          'Description': ''}
    '''
    sock = socket.socket()
    sock.connect((address, port))
    sock.send('{"cmd":"get_token"}'.encode())
    resp = json.loads(sock.recv(RECV_BUF_SIZE))
    return resp


def whatsminer_set_time_zone(token, address, port=4028):
    sock = socket.socket()
    sock.connect((address, port))
    sock.send('"cmd":"set_zone", "timezone": "UTC-0", "zonename": "Etc/UTC", "token": "{}"'.format(token).encode())
    resp = json.loads(sock.recv(RECV_BUF_SIZE))
    return resp


def main():
    parser = argparse.ArgumentParser(description='Tool to get error codes from miner APIs')
    parser.add_argument("--start_ip", required=True)
    parser.add_argument("--end_ip", required=True)
    parser.add_argument("--password", required=True)

    args = parser.parse_args()
    start_ip_octets = args.start_ip.split('.')
    end_ip_octets = args.end_ip.split('.')
    assert len(start_ip_octets) == 4
    assert len(end_ip_octets) == 4

    logging.basicConfig(level=logging.INFO)

    for octet0 in range(int(start_ip_octets[0]), int(end_ip_octets[0])+1):
        for octet1 in range(int(start_ip_octets[1]), int(end_ip_octets[1])+1):
            for octet2 in range(int(start_ip_octets[2]), int(end_ip_octets[2])+1):
                for octet3 in range(int(start_ip_octets[3]), int(end_ip_octets[3])+1):
                    ip = '.'.join(map(str, [octet0, octet1, octet2, octet3]))
                    token = get_token(ip)
                    salt = token['Msg']['salt']
                    plaintxt = 'set_zone' + args.password + salt + str(time.time())
                    hashtxt = sha256(plaintxt.encode()).digest()
                    encodedtxt = b64encode(hashtxt)
                    token_token = encodedtxt[:8]
                    logging.warning('%s %s', ip, whatsminer_set_time_zone(token_token, ip))


if __name__ == "__main__":
    main()
