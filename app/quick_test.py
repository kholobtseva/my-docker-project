import logging
from pygelf import GelfUdpHandler

logger = logging.getLogger('quick_test')
logger.setLevel(logging.INFO)

handler = GelfUdpHandler(host='graylog', port=12201)
logger.addHandler(handler)

logger.info('QUICK TEST: Hello Graylog!')
print('Test sent!')