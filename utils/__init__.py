import os
import configparser

from utils.utils import mask_cpf
from utils.utils import unmask_cpf
from utils.validation import is_valid_cpf
from utils.validation import is_valid_email


#: ConfigParser variable that holds all environment configuration of this project.
env = configparser.ConfigParser()
env.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "env.ini"))
