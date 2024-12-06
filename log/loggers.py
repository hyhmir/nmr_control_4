'''Logging of events and messages to files/cmd/email'''

import logging
import logging.handlers


def Configure_logger(logger):
    '''Creates all desired configurations and adds to logger'''

    program_email = 'nejc.jansa@ijs.si'
    my_email = 'nejc.jansa@ijs.si'

    # Default stream handler
    logging.basicConfig(level=logging.DEBUG,
        format='%(levelname)s: %(message)s')

    # Create different handlers for different ways of forwarding logs
    #s_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('log_files\\app.log')
    m_handler = logging.handlers.SMTPHandler('mailbox.ijs.si', program_email,
        [my_email], 'NMR 16T - CRITICAL!')

    #s_handler.setLevel(logging.DEBUG) # Writes all in cmd
    f_handler.setLevel(logging.INFO) # Logs informative and higher to file
    m_handler.setLevel(logging.CRITICAL) # Sends critical on email

    # Set the format of the handlers
    #s_format = logging.Formatter('%(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    m_format = logging.Formatter('%(asctime)s - %(levelname)s:\n%(message)s')
    #s_handler.setFormatter(s_format)
    f_handler.setFormatter(f_format)
    m_handler.setFormatter(m_format)

    # Add the handlers to the logger
    #logger.addHandler(s_handler)
    logger.addHandler(f_handler)
    logger.addHandler(m_handler)

    print('Configuring my_logger')



def Test_logger(logger):
    '''Tests the different responses of loggers'''
    logger.debug('I am debugging')
    logger.info('I am informing')
    logger.warning('I am warning you!')
    logger.error('This is an error!')
    logger.critical('Holy shit things are going critical!!!!')



def Configure_informer(logger):
    '''Sets up a logger for informative emails (end of measurement, etc)'''

    program_email = 'nejc.jansa@ijs.si'
    my_email = 'nejc.jansa@ijs.si'

    m_handler = logging.handlers.SMTPHandler('mailbox.ijs.si', program_email,
        [my_email], 'NMR 16T - INFO')
    m_handler.setLevel(logging.INFO) # Sends information on email
    m_format = logging.Formatter('%(asctime)s - %(levelname)s:\n%(message)s')
    m_handler.setFormatter(m_format)
    logger.addHandler(m_handler)



# Initiate the logger
logger = logging.getLogger('log')
Configure_logger(logger)
informer = logging.getLogger('info')
Configure_informer(informer)
# Remove low logs from matplotlib
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)



if __name__ == "__main__":
    '''Executes when this is the main aplication'''
    Test_logger(logger)
    informer.info('Measurement complete')

