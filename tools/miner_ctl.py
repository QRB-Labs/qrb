#!/usr/bin/python3
'''
For WhatsMiner API,
- enable API access via WhatsMinerTool
- change the default password via WhatsMinerTool
- must use the "super" account in API v3, not "admin"

Uses https://github.com/QRB-Labs/PyWhatsminer
'''

import argparse
import ipaddress
import json

from pywhatsminer.core import WhatsminerAccessToken, WhatsminerAPI
import miner_lib
import qrb_logging


def whatsminer_reboot(access_token):
    resp = WhatsminerAPI.exec_command(access_token, "reboot")
    miner_lib.check_response(resp)
    return resp


def whatsminer_set_power_mode(access_token):
    resp = WhatsminerAPI.exec_command(access_token, "set_normal_power")
    miner_lib.check_response(resp)
    return resp


def whatsminer_set_time_zone(access_token):
    resp = WhatsminerAPI.exec_command(access_token, "set_zone", {"timezone": "UTC", "zonename": "Etc/UTC"})
    miner_lib.check_response(resp)
    return resp


def main():
    parser = argparse.ArgumentParser(description='Tool to send commands to miners write API')
    parser.add_argument("--start_ip", required=True)
    parser.add_argument("--end_ip", required=False)
    parser.add_argument("--password", required=True)
    parser.add_argument("--output", choices=['logstash', 'syslog'], default='logstash')

    args = parser.parse_args()
    if not args.end_ip:
        args.end_ip = args.start_ip

    my_logger = qrb_logging.get_logger("miner_ctl", args.output)

    for i in range(int(ipaddress.IPv4Address(args.start_ip)),
                   int(ipaddress.IPv4Address(args.end_ip))+1):
        ip = str(ipaddress.ip_address(i))
        try:
            access_token = WhatsminerAccessToken(ip, 4028, args.password)
            api_version = miner_lib.whatsminer_get_version(ip)
            api_version.update({"ip_address": ip})
            my_logger.debug(api_version)
            assert api_version['Msg']['api_ver'].split('.')[0] == '2', \
             "Unsupported WhatsMiner API version {}".format(api_version['Msg']['api_ver'])

            for fn in [
#                    whatsminer_set_time_zone,
#                    whatsminer_set_power_mode,
                    whatsminer_reboot
            ]:
             resp = fn(access_token)
             resp.update({"ip_address": ip,
                          "action": fn.__name__})
             my_logger.warning(resp)
        except OSError as e:
             my_logger.error({"ip_address": ip,
                              'code': -e.errno,
                              'message': '{}'.format(e)})
        except Exception as e2:
            record = {"ip_address": ip}
            try:
                # pywhatsminer throws Exception where the arg is just the json response bytes
                # we try to extract the response into our log record
                record.update(json.loads(e2.args[0]))
            except Exception as e3:
                record["message"] = f"{e2}"
            my_logger.error(record)


if __name__ == "__main__":
    main()
