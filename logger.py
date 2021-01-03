import sys
import logging


def get_logger(name):

    log = logging.getLogger(name)
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setLevel(logging.NOTSET)
    formatter = logging.Formatter('%(asctime)s [%(levelname)7s]: %(message)s')
    out_hdlr.setFormatter(formatter)

    log.addHandler(out_hdlr)
    log.setLevel(logging.DEBUG)

    return log
