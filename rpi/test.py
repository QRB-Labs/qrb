from qrb_logging import get_logger

mylogger = get_logger("rpi_testing")
mylogger.warning({"message": "Fake ON"})
mylogger.info({"Temperature": 12.5})
mylogger.error("plain error")
