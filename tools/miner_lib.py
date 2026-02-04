import json
import socket
from datetime import datetime

RECV_BUF_SIZE=1400


class MinerAPIError(Exception):
    def __init__(self, resp):
        self.resp = resp


def check_response(resp):
    if type(resp['STATUS']) == list:  # teraflux
        status = resp['STATUS'][0]
    else:  # whatsminer
        status = resp
    if status.get('STATUS') != 'S':
        raise MinerAPIError(status)


def send_json(json_cmd, address, port):
    with socket.socket() as sock:
        sock.connect((address, port))
        sock.send(json_cmd.encode())
        recv_bytes = b''
        while True:
            chunk = sock.recv(RECV_BUF_SIZE)
            if not chunk:
                break
            recv_bytes += chunk
        # some miners, e.g. antminer, append null character 0x00 to the end of the resppnse
        if recv_bytes[-1] == 0x00:
            recv_bytes = recv_bytes[0:-1]
        resp = json.loads(recv_bytes)
        return resp


def whatsminer_get_version(address, port=4028):
    return send_json('{"cmd":"get_version"}', address, port)


def whatsminer_get_miner_info(address, port=4028):
    """Returns a dict with keys: 'ip',  'mac',  'minersn', 'powersn', etc.
    """
    resp = send_json('{"cmd":"get_miner_info"}', address, port)
    check_response(resp)
    return resp['Msg']


def teraflux_get_version(address, port=4028):
    return send_json('{"command":"version"}', address, port)


def teraflux_get_miner_info(address, port=4028):
    """
    Returns a dict with keys: SerialNo, ip, mac, model, CBSerialNo, ChassisSerialNo, etc.
    """
    resp = send_json('{"command":"ipreport"}', address, port)
    check_response(resp)
    return resp['IPReport'][0]


def get_token(address, port=4028):
    '''
    Get data needed to construct a token for writeable API.

    @returns a dict like {'STATUS': 'S',
                          'When': 1754491136,
                          'Code': 134,
                          'Msg': {'time': '1136', 'salt': 'BQ5hoXV9', 'newsalt': '9tfYlMf9'},
                          'Description': ''}
    '''
    return send_json('{"cmd":"get_token"}', address, port)


def get_summary(address, port=4028):
    return send_json('{"command":"summary"}', address, port)


def edevs(address, port=4028):
    """
    Get detailed report on hash boards.
    Yields a dictionary for each board
    """
    resp = send_json('{"command": "edevs"}', address, port)
    check_response(resp)

    for r in resp['DEVS']:
        r['ip_address'] = address
        if 'When' in resp['STATUS'][0]:
            r['datetime'] = datetime.fromtimestamp(resp['STATUS'][0]['When'])
        r['code'] = resp['STATUS'][0].get('Code', 9)
        r['message'] = resp['STATUS'][0]['Msg']
        if r.get('Enabled') == 'Y':
            r['Enabled'] = True  # whatsminer returns 'Y'/'N' instead of boolean
        if r.get('Enabled') == 'N':
            r['Enabled'] = False
        yield r


def get_pools(address, port=4028):
    """
    Get the currently active pool config
    Yields for each pool, a dictionary with keys: URL, User, etc
    Testeed on whatsminer, luxminer, teraflux, antminer
    """
    resp = send_json('{"command": "pools"}', address, port)
    check_response(resp)

    for r in resp['POOLS']:
        r['ip_address'] = address
        if 'When' in resp['STATUS'][0]:
            r['datetime'] = datetime.fromtimestamp(resp['STATUS'][0]['When'])
        if 'Last Share Time' in r:
            # antminer returns this field as a time of day e.g. "18:03:44",
            try:
                r['Last Share Time'] = int(r['Last Share Time'])
            except ValueError:
                last_share_time = datetime.combine(date.today(), datetime.strptime(r['Last Share Time'], "%H:%M:%S").time())
                r['Last Share Time'] = last_share_time.timestamp()
        r['code'] = resp['STATUS'][0].get('Code', 9)
        r['message'] = resp['STATUS'][0]['Msg']
        yield r
