import sys
import logging
import configparser

def setup_logger():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger()


def read_config(path='config.ini'):
    config = configparser.ConfigParser()
    config.read(path)
    return config['DEFAULT']

config = read_config()
logger = setup_logger()
