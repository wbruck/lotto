import logging
def get_logger(name:str):
    logger = logging.getLogger(name)

    
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger

