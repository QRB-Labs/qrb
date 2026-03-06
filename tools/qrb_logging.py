import logging
import logging.handlers
from datetime import datetime
from logstash import TCPLogstashHandler
from logstash.formatter import LogstashFormatterBase


class LogstashFormatter(LogstashFormatterBase):
    def format(self, record):
        message = record.msg
        message['@timestamp'] =  datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        message.setdefault('code', message.get('Code'))
        message.setdefault('message', message.get('Msg'))
        if 'When' in message:
            message['datetime'] = datetime.fromtimestamp(message['When'])

        # some miners return difficulty as a 256-bit number, while others
        # return that divided by 2^32 as network difficulty. if >= 2^64,
        # it can't be ingested by elasticsearch where it is a long.
        # we delete it for now. TODO: normalize across miners as a long
        message.pop('Difficulty Accepted', None)
        message.pop('Difficulty Rejected', None)

        host = {}
        if 'ip_address' in message:
            host['ip'] =  message['ip_address']
            del message['ip_address']
        if 'mac' in message:
            host["mac"] = message['mac']

        message.update({
            'host': host,
            'path': record.pathname,
            'tags': self.tags,
            'type': self.message_type,
            'level': record.levelname,
            'logger_name': record.name,
        })

        return self.serialize(message)


def get_logger(logger_name, output_type):
    my_logger = logging.getLogger(logger_name)
    my_logger.setLevel(logging.DEBUG)

    if output_type == 'syslog':
        my_logger.addHandler(logging.handlers.SysLogHandler('/dev/log'))
    if output_type == 'logstash':
        handler = TCPLogstashHandler(host='192.168.6.100', port=5959)
        handler.setFormatter(LogstashFormatter())
        my_logger.addHandler(handler)

    return my_logger
