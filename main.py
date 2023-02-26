from config import *
from personal_equipment import PersonalEquipment
from category import Category
from cell import Cell
from utils import * 
import pandas as pd 
import pprint
import time
def main():
	start_time = time.time()

	inflow_setting = create_inflow_setting(OUTFLOW_SETTING)
	
	print("Scenario will be created")

	cells = create_scenerio(inflow_setting,OUTFLOW_SETTING)

	print("Scenario created, simulation will start")

	# time iteration and creating the data frame
	df = simulation(cells)

	print("Simulation ended, data will be exported")

	df.to_csv('../data/exponential.csv',index = False)
	print("Data export completed")
	print("--- %s seconds ---" % (time.time() - start_time))

def simulation(cells):
	multiplier = 1
	
	data = {
		't':[],
		'cell_id':[],
		'cat_id':[],
		'pe_id':[],
		'load':[],
		'has_anomaly':[]
		}

	mod = 30 
	mod_step = int(mod * 0.08)
	mod_smooth_period = 5 
	mod_smooth_counter = 0 
	num_anomaly = int(SIM_TIME * ANOMALY_PERCENTAGE)
	anomaly_steps = sorted(sample_with_minimum_distance(n = SIM_TIME - mod, k = num_anomaly, d = mod + 1  ))
	anomaly_step_ends = [x + mod for x in anomaly_steps]
	anomaly_idx = 0	

	for t in range(SIM_TIME):
		# Add random anomalities to data based on anomaly_idx
		has_anomaly = 0
		if anomaly_idx < num_anomaly:
			if t >= anomaly_steps[anomaly_idx] and t <= anomaly_step_ends[anomaly_idx] :
				has_anomaly = 1
				if mod_smooth_counter == 0: 
					multiplier = 1.002
				if mod_smooth_counter == mod_step*1: #1 - 2
					multiplier = 1.004
				if mod_smooth_counter == mod_step*2: #3 - 4
					multiplier = 1.008
				if mod_smooth_counter == mod_step*3: #4 - 7
					multiplier = 1.016
				if mod_smooth_counter == mod_step*4: # 6 - 9
					multiplier = 1.032
				if mod_smooth_counter == mod_step*5: # 8 - 12
					multiplier = 1.064
				if mod_smooth_counter == (mod - (mod_step*5)): 
					multiplier = 1.032
				if mod_smooth_counter == (mod - (mod_step*4)): 
					multiplier = 1.016
				if mod_smooth_counter == (mod - (mod_step*3)): 
					multiplier = 1.008
				if mod_smooth_counter == (mod - (mod_step*2)): 
					multiplier = 1.004
				if mod_smooth_counter == (mod - (mod_step*1)): 
					multiplier = 1.002
				if mod_smooth_counter == mod: 
					multiplier = 1
				mod_smooth_counter += 1
				
				if t == anomaly_step_ends[anomaly_idx]:
					anomaly_idx += 1 
					mod_smooth_counter = 0


		# Determine handover rates
		handover_rate = {}

		for cell in cells: 

			ho_rate_cat = {}
			for cat in cell.cat_list:

				ho_rate_pe = {}
				# In this loop, based on the SIM_TIME length, set the handover modes based on the time of the day.
				# In original scenario, One day consists of 96 ticks. (each 15 minutes is 1 sim time iteration)
				for pe in cat.pe_list:
					if t % 96 >= 0 and t % 96 < 24:
						pe.set_handover_mode(0)
					elif t % 96 >= 24 and t % 96 < 28:
						pe.set_handover_mode(4)
					elif t % 96 >= 28 and t % 96 < 38:
						pe.set_handover_mode(1)
					elif t % 96 >= 38 and t % 96 < 44:
						pe.set_handover_mode(2)
					elif t % 96 >= 44 and t % 96 < 52:
						pe.set_handover_mode(3)
					elif t % 96 >= 52 and t % 96 < 64:
						pe.set_handover_mode(2)
					elif t % 96 >= 64 and t % 96 < 80:
						pe.set_handover_mode(1)
					elif t % 96 >= 80 and t % 96 < 88:
						pe.set_handover_mode(4)
					elif t % 96 >= 88 and t % 96 < 96:
						pe.set_handover_mode(0)

					ho_rate_pe[pe.pe_id] = pe.get_normal_distribution()

				ho_rate_cat[cat.cat_id] = ho_rate_pe

			handover_rate[cell.id] = ho_rate_cat

		# now we need to assign handovers to other cells and categories.
		for cell_i_id, cell_j_id_list in OUTFLOW_SETTING.items():
			# first remove the load from cell_i 

			for cat in cells[cell_i_id].cat_list:
				for pe in cat.pe_list:
					pre_load = pe.load
					new_load = pre_load - handover_rate[cell_i_id][cat.cat_id][pe.pe_id]
					pe.set_load(new_load)
			# now add necessary load to others
			load_divider = len(cell_j_id_list)
			for cell_j_id in cell_j_id_list:
				for cat in cells[cell_j_id].cat_list:
					for pe in cat.pe_list:
						pre_load = pe.load
						new_load = pre_load + (handover_rate[cell_i_id][cat.cat_id][pe.pe_id] / load_divider)
						pe.set_load(new_load)

		# now loads are balanced, write information to dictionary so that we can convert it to pandas and csv

		for cell in cells:
			for cat in cell.cat_list:
				for pe in cat.pe_list:
					data['t'].append(t)
					data['cell_id'].append(cell.id)
					data['cat_id'].append(cat.cat_id)
					data['pe_id'].append(pe.pe_id)
					data['load'].append(pe.load*multiplier)
					data['has_anomaly'].append(has_anomaly)
	return pd.DataFrame(data)


# returns cell list
def create_scenerio(inflow_setting, outflow_setting):
	scenerio = []

	for x in range(CELL_NUMBER):

		cat_list = []

		for y in range(CAT_NUMBER):

			pe_load_dict = INITIAL_CONFIG[y]
			pe_list = []

			for z in range(PE_NUMBER):

				pe = PersonalEquipment(z,pe_load_dict[z])
				pe.assign_category(y)
				pe_list.append(pe)


			cat = Category(y,pe_list)
			cat_list.append(cat)

		cell = Cell(x, cat_list)
		cell.assign_flow_lists(inflow_setting[x],outflow_setting[y])
		cell.assign_handover_setting(HANDOVER_SETTING[x])
		scenerio.append(cell)
	return scenerio

def create_inflow_setting(outflow):
	# input type : {cell_id : [list of other cell ids]}
	# output type : {cell_id : [{cell_id: ratio }]}
	cell_ratios = {key: 1/len(value) for key, value in outflow.items()}
	return {key: [{v:cell_ratios[v]} for v in value] for key, value in outflow.items()}

def _print_scenario(cells):
	for cell in cells:
		print (f"Cell id: {cell.id} : ")
		for cat in cell.cat_list:
			print (f"Cat id: {cat.cat_id} : ")
			for pe in cat.pe_list:
				print(f"PE Name: {pe.pe_name} Load: {pe.init_load} Ho_param: {pe.handover_param} Ho_mean: {pe.handover_mean} Ho_var: {pe.handover_var}")

		print()
if __name__ == '__main__':
	main()