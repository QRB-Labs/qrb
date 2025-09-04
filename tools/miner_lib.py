import json
import socket
from datetime import datetime

RECV_BUF_SIZE=4096


class MinerAPIError(Exception):
    def __init__(self, message, resp):
        super().__init__(message)
        self.resp = resp


def check_response(resp):
    if type(resp['STATUS']) == list:  # teraflux
        status = resp['STATUS'][0]
    else:  # whatsminer
        status = resp
    if status.get('STATUS') != 'S':
        raise MinerAPIError("", resp)


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
        assert len(recv_bytes) < RECV_BUF_SIZE
        resp = json.loads(recv_bytes)
        return resp


def whatsminer_get_version(address, port=4028):
    return send_json('{"cmd":"get_version"}', address, port)


def teraflux_get_version(address, port=4028):
    return send_json('{"command":"version"}', address, port)


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
    Get temperature of miner
    Yields a dictionary
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
