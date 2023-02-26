class Cell(object):
	"""
	docstring for Cell
	string or int : id
	list: inflow_list : adjacency matrix for inflow
	list: outflow_list : adjacenct list but reverse, will give how much handover this cell will take (might be a dict later)
	list: cat_list = category list belong cell i 
	load: calculated from categories' total loads.
	list : cat_percentage [class Category]
	
	"""
	def __init__(self,id, cat_list ):
		self.id = id
		self.cat_list = cat_list
		self.load = self.calculate_load()

	def calculate_load(self):
		loads = [x.load for x in self.cat_list]
		return sum(loads)

	def assign_flow_lists(self,inflow_list, outflow_list):
		self.inflow_list = inflow_list
		self.outflow_list = outflow_list
	def assign_handover_setting(self, handover_setting):
		self.handover_setting = handover_setting
		self.modify_cats_handover(handover_setting)

	def modify_cats_handover(self,handover_setting):
		for cat in self.cat_list:
			cat.assign_handover_setting(handover_setting)
