import logging
from logstash import TCPLogstashHandler
from logstash.formatter import LogstashFormatterBase
import socket


class LogstashFormatter(LogstashFormatterBase):
    def format(self, record):
        if isinstance(record.msg, dict):
            message = record.msg
            message.update({
                'path': record.pathname,
                'level': record.levelname,
                'logger_name': record.name,
            })
        else:
            message = {"@message" : record.msg}
        message['@source_host'] = socket.gethostname()
        return self.serialize(message)

    
def get_logger(logger_name):
    my_logger = logging.getLogger(logger_name)
    my_logger.setLevel(logging.DEBUG)
    handler = TCPLogstashHandler(host='192.168.6.100', port=5959)
    handler.setFormatter(LogstashFormatter()) 
    my_logger.addHandler(handler)
    return my_logger


mylogger =  get_logger("rpi_testing")
mylogger.warning({"message": "Fake ON"})
mylogger.info({"Temperature": 12.5})
mylogger.error("plain error")
