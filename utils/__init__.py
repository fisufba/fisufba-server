import os
import configparser

env = configparser.ConfigParser()
env.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "env.ini"))
