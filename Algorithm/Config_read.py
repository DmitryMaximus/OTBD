import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.realpath(__file__))+"\config.ini",encoding='utf-8')
confdict = {section: dict(config.items(section)) for section in config.sections()}