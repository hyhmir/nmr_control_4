'''Test using of logger from different module'''

#from logger import my_logger
import loggers    # Done once in main?

import logging
logger = logging.getLogger('log')     # Works in any module
# Alternatively:
#from logger import my_logger    # Path is module dependent...

logger.debug('I am debugging')
logger.info('I am informing')
logger.warning('I am warning you!')
logger.error('This is an error!')
logger.critical('Holy shit things are going critical!!!!')

# This configuration seems to work.

logging.debug('crap')