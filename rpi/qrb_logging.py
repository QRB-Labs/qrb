import logging
import logging.handlers
from logstash import TCPLogstashHandler
from logstash.formatter import LogstashFormatterBase
import socket


class LogstashFormatter(LogstashFormatterBase):
    def format(self, record):
        if isinstance(record.msg, dict):
            message = record.msg
        else:
            message = {"@message" : record.msg}
        message.update({
            '@source_host': socket.gethostname(),
            'path': record.pathname,
            'level': record.levelname,
            'logger_name': record.name,
        })
        return self.serialize(message)


def get_logger(logger_name):
    mylogger = logging.getLogger(logger_name)
    handler = TCPLogstashHandler(host='192.168.6.100', port=5959)
    handler.setFormatter(LogstashFormatter())
    mylogger.addHandler(handler)
    mylogger.setLevel(logging.INFO)
    return mylogger
