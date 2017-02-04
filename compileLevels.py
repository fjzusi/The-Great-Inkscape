import levelModule
import pickle
from config import *

print "Compiling Levels"

for index in range(1, NUM_LEVELS+1):
	level = levelModule.Level(index)
	levelModule.saveToPickle(level)
	print "Level "+str(index)+" compiled"

print "Levels Compiled"
raw_input("Press any key to continue")
	