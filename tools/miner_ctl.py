#!/usr/bin/python3
'''
For WhatsMiner API,
- enable API access via WhatsMinerTool
- change the default password via WhatsMinerTool
- must use the "super" account in API v3, not "admin"
'''

import argparse
import json
import logging
import socket
import time

from hashlib import sha256
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


RECV_BUF_SIZE=4096


def get_version(address, port=4028):
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
    sock.send('{"cmd":"get_version"}'.encode())
    resp = json.loads(sock.recv(RECV_BUF_SIZE))
    return resp


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


def whatsminer_set_time_zone_v3(password, salt, ip, port=4028):
    command = "set_zone"
    timestamp = int(time.time())
    hash_string = f"{command}{password}{salt}{timestamp}"
    hashtxt = sha256(hash_string.encode('utf-8')).digest()
    encodedtxt = b64encode(hashtxt).decode('utf-8')
    logging.debug(encodedtxt)
    token = encodedtxt[:8]

    param = {
        "timezone": "UTC-0", 
        "zonename": "Etc/UTC"
    }
    param_json_string = json.dumps(param)
    padded_data = pad(param_json_string.encode('utf-8'), AES.block_size)
    aes_key = hashtxt
    assert len(aes_key) == 32
    cipher = AES.new(aes_key, AES.MODE_ECB)
    encrypted_data = cipher.encrypt(padded_data)
    encrypted_param_b64 = b64encode(encrypted_data).decode('utf-8')

    payload = """{{
        "cmd": "set_zone",
        "ts": "{}",
        "token": "{}",
        "account": "super",
        "param": "{}"
    }}""".format(timestamp, token, encrypted_param_b64)
    logging.debug(payload)
    
    with socket.socket() as sock: 
        sock.connect((ip, port))
        sock.settimeout(5)
        sock.send(payload.encode())
        resp = json.loads(sock.recv(RECV_BUF_SIZE))
        return resp


def whatsminer_set_time_zone_v2(password, salt, ip, port=4028):
    command = "set_zone"
    timestamp = int(time.time())
    hash_string = f"{command}{password}{salt}{timestamp}"
    hashtxt = sha256(hash_string.encode('utf-8')).digest()
    encodedtxt = b64encode(hashtxt).decode('utf-8')
    logging.debug(encodedtxt)
    token = encodedtxt[:8]

    payload = json.dumps(
        { "cmd": "set_zone",
          "token": token,
          "zone": "Etc/UTC",
          "id": 1
        })  + "\n"
    logging.debug(payload)
    payload_bytes = payload.encode('utf-8')
    
    with socket.socket() as sock: 
        sock.settimeout(5)
        sock.connect((ip, port))
        # sock.sendall(len(payload_bytes).to_bytes(4, 'little'))
        sock.sendall(payload_bytes)
        # resp_len = int.from_bytes(sock.recv(4), 'little')
        resp = json.loads(sock.recv(RECV_BUF_SIZE).decode('utf-8'))
        logging.debug(json.dumps(resp))
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

    logging.basicConfig(level=logging.DEBUG)

    for octet0 in range(int(start_ip_octets[0]), int(end_ip_octets[0])+1):
        for octet1 in range(int(start_ip_octets[1]), int(end_ip_octets[1])+1):
            for octet2 in range(int(start_ip_octets[2]), int(end_ip_octets[2])+1):
                for octet3 in range(int(start_ip_octets[3]), int(end_ip_octets[3])+1):

                    ip = '.'.join(map(str, [octet0, octet1, octet2, octet3]))

                    api_version = get_version(ip)
                    logging.debug(api_version)
                    assert api_version['Msg']['api_ver'].split('.')[0] == '2', \
                        "Unsupported WhatsMiner API version {}".format(api_version['Msg']['api_ver'])

                    token_info = get_token(ip)
                    logging.debug(token_info)
                    assert token_info['STATUS'] == 'S', "Unable to get token: {}".format(token_info)

                    whatsminer_set_time_zone_v3(args.password, token_info['Msg']['salt'], ip)




if __name__ == "__main__":
    main()
