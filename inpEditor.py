# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 22:04:45 2023

@author: AdilK

"""
import os
import openpyxl
import numpy as np
#import math

"""change this to True if you want to add plasticity"""
plastic_info = True

""" change this to True if there is excel file for plasticity """
excel_data = False 
""" change this to True if you want to implement hall-petch equation"""
hall_petch=True
""" change this to True if you want to  implement plastic data manually"""
manual_entry=False


#Set working directory
dir_path = 'C:/Users/adminlocal/Desktop/Data'
os.chdir(dir_path)
filename = "Job-1.inp"

material_number = None

#Insert the input and assign it to a variable
with open("Job-1.inp", "r") as f:
    file_contents = f.read()

# External plastic data import excel file
data = ""
def read_table_from_excel(filename, sheetname, cell_range):
    # Load XML file
    if excel_data == True:
        workbook = openpyxl.load_workbook(filename)
        worksheet = workbook[sheetname]
        data = []
        for row in worksheet[cell_range]:
            row_data = []
            for cell in row:
                row_data.append(cell.value)
            data.append(row_data)
            
    return data
if excel_data == True:
    data = read_table_from_excel("data_plastic.xlsx", "Table1", "A1:B5")

def read_input_file(filename):
    # read node table
    with open(filename, 'r') as f:
        node_lines = []
        read_nodes = False
        for line in f:
            if '*Node' in line:
                read_nodes = True
            elif '*' in line and read_nodes:
                break
            elif read_nodes:
                node_lines.append(line)
        nodes = np.loadtxt(node_lines, delimiter=',')

    # read element table
    with open(filename, 'r') as f:
        elem_lines = []
        read_elems = False
        for line in f:
            if '*Element, type=CPS3' in line:
                read_elems = True
            elif '*' in line and read_elems:
                break
            elif read_elems:
                elem_lines.append(line)
        elems = np.loadtxt(elem_lines, delimiter=',', dtype=int)

    # read elset grain materials
    with open(filename, 'r') as f:
        elset_data = {}
        current_elset = None
        for line in f:
            line = line.strip()
            if line.startswith('*Elset, elset='):
                current_elset = line.split('=')[1]
                elset_elements = []
                elset_data[current_elset] = elset_elements
            elif line.startswith("** Section"):
                break
            elif current_elset is not None and line:
                element_ids = [int(x) for x in line.split(',') if x.strip()]
                elset_data[current_elset].extend(element_ids)

    return nodes, elems, elset_data


def calculate_areas(elset_data, nodes, elems):
    areas = {}
    for elset_name, elset_elems in elset_data.items():
        area_sum = 0.0
        for elem_id in elset_elems:
            node_ids = elems[elem_id - 1][1:]
            coords = nodes[node_ids - 1, 1:]
            x1, y1 = coords[0]
            x2, y2 = coords[1]
            x3, y3 = coords[2]
            area = abs(0.5 * ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)))
            area_sum += area
        areas[elset_name] = area_sum
    return areas

nodes, elems, elset_data = read_input_file(filename)
areas = calculate_areas(elset_data, nodes, elems)

areas_array=list(areas.values())

def add_hall_petch(sigma_0, k_y, areas_array):
    
    sigma_0 = 270 #MPa
    k_y = 2000 #MPa.um^0.5
    d = 2*np.sqrt(areas_array)
    sigma_y = sigma_0 + k_y * d**(-0.5)
    
    return sigma_y
sigma_y = add_hall_petch(270, 2000, areas_array)
sigma_y_zeros = np.zeros((247,1))
sigma_y_final = np.concatenate((sigma_y.reshape(-1, 1), sigma_y_zeros), axis=1)



#Checks if the output file name exists
filename = "Job-1.inp"
if os.path.exists(filename):
    i = 1
    while os.path.exists(f"{filename.split('.')[0]}_{i}.inp"):
        i += 1
    filename = f"{filename.split('.')[0]}_{i}.inp"


#Change all material properties with a single value
def add_elastic_info(file_contents, modulus, poisson):
    new_file_contents = ""
    for line in file_contents.split("\n"):
        if "*Material, name=" in line:
            new_file_contents += line + "\n"
            next_line = file_contents.split("\n")[file_contents.split("\n").index(line)+1]
            if not "*Elastic" in next_line:
                new_file_contents += f"*Elastic\n{modulus}, {poisson}\n"
        else:
            new_file_contents += line + "\n"
    return new_file_contents, modulus, poisson

#Create a new file with updated material properties
new_file_contents, modulus, poisson = add_elastic_info(file_contents, 300, 0.3)


def add_plastic_info(new_file_contents, new_plastic_data, plastic_info):
    another_file_contents = ""
    if excel_data == True:
        new_plastic_data = data
    if hall_petch == True:
        new_plastic_data = sigma_y_final
    if plastic_info:   
        for line in new_file_contents.split("\n"):
            if "*Material, name=MATERIAL-" in line:
                material_number = int(line.split("-")[-1])
            if f"{modulus}, {poisson}" in line:
                another_file_contents += line + "\n"
                next_line = new_file_contents.split("\n")[new_file_contents.split("\n").index(line)+1]
                if not "*Plastic" in next_line:
                    plastic_data = ""
                    another_file_contents += "*Plastic\n"
                    if hall_petch == True:
                        for row in new_plastic_data[material_number]:
                            plastic_data += f"{row}, "
                        plastic_data = plastic_data[:-2] + "\n"
                    else:
                        for row in new_plastic_data:
                            plastic_data += f"{row[0]}, {row[1]}\n"
                    another_file_contents += plastic_data
            else:
                another_file_contents += line + "\n"
    else:
        another_file_contents =  new_file_contents      
    return another_file_contents


if excel_data==True:
    another_file_contents = add_plastic_info(new_file_contents, data, plastic_info = True)
elif hall_petch==True:
    another_file_contents = add_plastic_info(new_file_contents, sigma_y_final, plastic_info = True)
elif manual_entry==True:
    new_plastic_data=[ [200., 0.], [220., 0.005] ]
    another_file_contents = add_plastic_info(new_file_contents,new_plastic_data, plastic_info = True)


#Write the new file
with open(filename, "w") as f:
    if plastic_info == False:
        f.write(new_file_contents)
    else: 
        f.write(another_file_contents)
    