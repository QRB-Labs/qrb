from logstash import TCPLogstashHandler
import logging

mylogger =  logging.getLogger(__name__)
handler = TCPLogstashHandler(host='192.168.6.100', port=5959)
mylogger.addHandler(handler)

mylogger.warning("soupe")
mylogger.info("a l'oignon")
mylogger.error("y croutons")
