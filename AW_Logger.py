import os
from datetime import datetime
import logging

########################################################################
class Single_Line_Formatter(logging.Formatter):
	def __init__(self):
		template_format   = '%(levelname)s "%(asctime)s "%(message)s" :: %(module)s - %(funcName)s - %(lineno)d'
		logging.Formatter.__init__(self,fmt=template_format, datefmt="%Y-%m-%d-%H-%M-%S")
		
########################################################################
class Single_Line_Handler(logging.FileHandler):
	#----------------------------------------------------------------------
	def __init__(self, filename, mode='a', encoding=None, delay=0):
		""""""
		super(Single_Line_Handler, self).__init__(filename, mode, encoding, delay)
		
########################################################################
class Single_Line_Logger(logging.Logger):
	""""""
	def __init__(self,name=None):
		logging.Logger.__init__(self,name)
		self.setLevel(level)

def create_Logger(name, filename, level=logging.WARNING, mode='w', encoding=None, delay=0):
	logger   = logging.getLogger(name)
	handler  = Single_Line_Handler(filename, mode, encoding, delay)
	formater = Single_Line_Formatter()
	
	logger.setLevel(level)
	handler.setFormatter(formater)
	logger.addHandler(handler)
	
	return logger

def get_Logger(name):
	logger   = logging.getLogger(name)
	return logger

