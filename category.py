from config import *
class Category(object):
	"""
	docstring for Category
	subsCats will be modeled here
	string or int id - id can be in this format: 2 digits, First digit is id of cell it is connected Second one is normal cell id
	cell id: which cell this category will be belong to 
	cat id: personal cat_id
	list: pe_list : list of personal equipments (Personal equipments)
	int: total_load : total_load of cell i category j.
	"""
	def __init__(self, cat_id, pe_list):
		self.cat_id = cat_id
		self.cat_name = SUBS_CATS[cat_id]
		self.pe_list = pe_list
		self.load = self.calculate_load()

	def assing_cell(self, cell):
		self.cell_id = cell.id
		self.cell = cell

	def calculate_load(self):
		loads = [x.load for x in self.pe_list]
		return sum(loads)

	def assign_handover_setting(self, handover_setting):
		self.handover_setting = handover_setting
		self.modify_pe_handover(handover_setting)

	def modify_pe_handover(self,handover_setting):
		for pe in self.pe_list:
			pe.assign_handover_params(handover_setting)