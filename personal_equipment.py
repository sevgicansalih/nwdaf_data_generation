from config import *
from distribution import gaussian_distribution
class PersonalEquipment(object):
	"""
	docstring for PersonalEquipment
	string or int id - id can be in this format: 3 digits, First digit is id of cell it is connected Second one is category it is inside, 
	int: pe_id : which Personal Equipment (iot mobile bla bla)
	string : pe_name: auto_generated
	int: init_load : Under cell i category j what is the load  

	"""
	def __init__(self, pe_id, init_load):
		self.pe_id = pe_id
		self.pe_name = PERSONAL_EQUIPMENT_ID[pe_id] 	
		self.init_load = init_load
		self.ho_dist = gaussian_distribution
		self.load = init_load
		self.handover_mode = 0

	def assign_category(self,cat_id):
		self.cat_id = cat_id
		
	def assign_handover_params(self,handover_setting):
		self.handover_param = handover_setting[self.pe_id]
		self.update_handover_params()

	def update_handover_params(self):
		self.handover_mean = self.load * BASE_MEAN * self.handover_param[self.handover_mode]
		self.handover_var = self.load * BASE_VAR * self.handover_param[self.handover_mode]

	def set_load(self,load):
		self.load = load

	def set_handover_mode(self,handover_mode):
		self.handover_mode = handover_mode
		self.update_handover_params()
		
	def get_normal_distribution(self):
		return gaussian_distribution(self.handover_mean, self.handover_var)
