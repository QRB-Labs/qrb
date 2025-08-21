#!/usr/bin/python3
'''
For WhatsMiner API,
- enable API access via WhatsMinerTool
- change the default password via WhatsMinerTool
- must use the "super" account in API v3, not "admin"

Uses https://github.com/QRB-Labs/PyWhatsminer
'''

import argparse
import json
import logging
from pywhatsminer.core import WhatsminerAccessToken, WhatsminerAPI

import miner_lib



def whatsminer_set_time_zone(password, ip, port=4028):
    access_token = WhatsminerAccessToken(ip, port, password)
    resp = WhatsminerAPI.exec_command(access_token, "set_zone", {"timezone": "UTC", "zonename": "Etc/UTC"})
    logging.info(f"{ip}: {json.dumps(resp)}")
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

                    try:
                        api_version = miner_lib.whatsminer_get_version(ip)
                        logging.debug(f"{ip}: {api_version}")
                        assert api_version['Msg']['api_ver'].split('.')[0] == '2', \
                            "Unsupported WhatsMiner API version {}".format(api_version['Msg']['api_ver'])

                        whatsminer_set_time_zone(args.password, ip)
                    except OSError as e:
                        logging.error(f"{ip}: {e}")
                    except Exception as e2:
                        logging.error(f"{ip}: {e2}")



if __name__ == "__main__":
    main()
