# inpEditor
Abaqus input file editor 
@adilk

## **What you can do with this .inpEditor module:

You can either add elasticity only (Young's modulus and Poisson ratio), 
or both elasticity and plasticity (yield stress and plastic strain) to .inp file 
for all grains.
Calculate grain size, grain area and implement the related Hall-Petch law and 
other characteristic properties.
At the moment, since we do not specify any hardening law to use, 
there is no further implementation for hardening law. The .inp file will not 
be overwritten but another file will be created instead for the safety of 
original input file. Also, note that the area calculation is based on CPS3 
(Three node plane stress element) type of elements which is trianglular element type.
If you have other type of elements but triangular, in this case, we need to develop another 
formula to calculate the area for that particular case.

## **How it works:
First, make sure you have set the working directory correctly and that 
the name of the .inp file matches. By default, it is named *Job-1.inp*.


### *To add elasticity only, jump to line #164 to set the modulus and Poisson ratio. 
Make sure that the value of "plastic_info" is set to False and run the code.

### *To add plasticity, set "plastic_info" to True on line #14. You have three options:

-Data import from an Excel file
-Manual data entry
-Data calculation through inpEditor from the .inp mesh file.

### *Importing from an Excel file:
If you have your hardening law defined in an Excel file, follow these steps:
1)Set *excel_data* to True on line #17
2)Jump to line #51 and change the file name, sheet name, and data interval accordingly.
3)Make sure your data format is given with dot decimal.


### *Manual data entry:
On line #21, change *manual_entry* to True and make sure the others(excel_data, 
hall_petch) are False.
1)Move to line #195, change the data as you like to. 
2)Change the part "[200., 0.], [220., 0.005] " accordingly.

### *Data calculation through inpEditor:
---
Here, before starting, note that this code only works if your mesh file has
 *elset* material groups that corresponds to each individual grains. 
 If not, the code will not find the grains since grains will not be pre-defined.
However, if you want to define each grains (*elset* objects) manually, 
in your input file, you can use the following format:
"
*Elset, elset=MATERIAL-0
  723,  724,  753
*Elset, elset=MATERIAL-1
  693,  719,  720, 2985
*Elset, elset=MATERIAL-2
  698,  721
*Elset, elset=MATERIAL-3
  711,  712,  713,  739,  740,  741,  742,  743
*Elset, elset=MATERIAL-4
...
...

"
This part comes after the elements connectivity table. You can name elset objects 
as you wish, here better to define as MATERIAL or GRAIN. Each numbers represent 
the mesh elements.
---
In case you have *elset* objects defined, set the hall_petch to True on line 19 and
the code should work perfectly and create another file named *Job-1_1.inp*.

## Change existing Young's modulus and Poisson's ratio
The function "change_data" allows to change the existing Young's modulus and Poisson's ratio for all grains. To do that, 
make sure the data_change on line #13 is set True. Then move to line #158 and #168. Line #158 is the old values of Young's modulus and Poisson's ratio. Line #168 is the new ones you intend to change.
