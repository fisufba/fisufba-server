import os
import configparser


#: ConfigParser variable that holds all environment configuration of this project.
env = configparser.ConfigParser()
env.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "env.ini"))
