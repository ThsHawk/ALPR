import time
import sys
import pprint
from Alpr import Alpr

if len(sys.argv) < 2 :
    print("Err: no path.")
    exit()

inst = Alpr(sys.argv[1])
text = inst.recognize()
pprint(text)

