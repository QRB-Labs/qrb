import json
import socket


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
    sock.send(json.dumps({"cmd":"get_token"}).encode())
    resp = json.loads(sock.recv(RECV_BUF_SIZE))
    return resp


def get_summary(address, port=4028):
    sock = socket.socket()
    sock.connect((address, port))
    sock.send('{"command":"summary"}'.encode())
    resp = json.loads(sock.recv(RECV_BUF_SIZE))
    return resp
