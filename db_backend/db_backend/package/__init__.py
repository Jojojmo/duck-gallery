import sys
from pathlib import Path

# Adiciona o caminho absoluto do diretório do package ao sys.path
sys.path.append(str(Path(__file__).parent.resolve()))

from Constraints_rules import *
from Save_image import *
from Insert import *
from Schemas import *
from Utils import *