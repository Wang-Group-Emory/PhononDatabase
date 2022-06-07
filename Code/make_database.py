'''
Matt Myers
09/28/2021
Senior Thesis
Final product

This program is the final culmination of all this work.
With this project there were a couple of goals that I wanted
accomplish. 

1:  Find the folder "NGSED" containg the data on anyones computer
2:  Filter the data so that only the helpful data was being put
    into the database
3:  Put the filtered information into a dictionary to be create
    the database
4: Create figures decided by user input
5:  Put the database into a cloud based engine that could handle
    it

*** Also worth noting this program will run in about 18 seconds if
    the "NGSED" folder is put in the C drive
'''
# Importing the libraries
import os
import shutil
import data_funcs as df
from options import *

# 1: Find the "NGSED" data and set current working directory
print("Searching for Data...", end='\n')
# df.find_and_set_directory()
os.chdir(rootdir)
print("Data Found\n")

# 2: Filter the data into a helpful format
# Filtering criteria 
#   Must include the needed_files and the excluded directories are in blacklist_dir
needed_files =['mylog','nonGaussED_eq_observables.txt', 'observableList.txt', 'varState.txt']
additional_dir = ['observable_name_list.txt','mylog','nonGaussED_eq_observables.txt', 
                'NGSED_iteration_variables.txt']
blacklist_dir = ['unconverged','without inversion symmetry','__MACOSX', 'NGSvariationalParams',
                 'old correct data', 'WarmUp','old data','withTprData','incompleted', 
                 'data assuming inversion symmetry', 'new','HubbardCal',
                 'U0allk','correct data without Delta','copy','backup']
# Filtering and returning the paths to the correct directories
#   Getting the filtered path information first
print('Searching for directories...')
print(f'Including: {needed_files} and {additional_dir}')
print('Not Including:',  blacklist_dir)
all_paths = df.dir_path_find(needed_files, blacklist_dir, additional_dir)
print("All directories found\n")

# 3:  Put the filtered information into a dictionary to be create the database
#   Going through each filtered path and extracting the data
data_list = []
for all_path in all_paths:
    # Setting the path to the desired directory
    os.chdir(all_path)
    data_list.append(df.make_dict_from_data(all_path))
updated_data = df.get_ground_state(data_list)

# 4: Making figures from the dictionaries
# Getting Necessary values for figure creation
if cmap or figs:
    # 4.5 Making Color Map
    c = 0
    g_key = 'g'
    tpr_key = 't\''
    gpr_key = 'g\''
    w_key = 'Freq (W)'
    dp_key = 'Doping (h)'
    g_vals = df.get_key_options(g_key, updated_data)
    tpr_vals = df.get_key_options(tpr_key,updated_data)
    gpr_vals = df.get_key_options(gpr_key, updated_data)
    w_vals = df.get_key_options(w_key, updated_data)
    dp_vals = df.get_key_options(dp_key, updated_data)
    var_list = [g_key, tpr_key, gpr_key, w_key, dp_key]
    val_list = [g_vals, tpr_vals, gpr_vals, w_vals, dp_vals]
    print('\nValues for creation of figures:\n')
    for val in val_list:
        print(f'{var_list[c]}: {val}')
        c+=1

if figs:
    # 4.5: Making figures
    print("\nCreating Figures...")
    figfoldorigin = f'{rootdir}\\figure_folder'
    try:
        shutil.rmtree(figfoldorigin)
        os.mkdir(figfoldorigin)
    except:
        pass
    for w in w_vals:
        for g in g_vals:
            for gpr in gpr_vals:
                for tpr in tpr_vals:
                    #print('\n\n')
                    desired_data = []
                    for entry in updated_data:
                        #print(entry)
                        if entry['Ground-State'] == 1 and entry['t\''] == tpr and entry['g'] == g and entry['Freq (W)'] == w and entry['g\''] == gpr:
                            figfoldw = f'{figfoldorigin}\\w={w}'
                            figfoldg = f'{figfoldw}\\g={g}'
                            figfoldgpr = f'{figfoldg}\\gpr={gpr}'
                            if not os.path.isdir(figfoldw):
                                os.mkdir(figfoldw)
                            if not os.path.isdir(figfoldg):
                                os.mkdir(figfoldg)
                            if not os.path.isdir(figfoldgpr):
                                os.mkdir(figfoldgpr)
                            desired_data.append(entry)
                    if not desired_data:
                        pass
                    else:
                        df.make_figures(desired_data, w, g, tpr, gpr)
    print('Figure Creation Complete')
elif cmap:
    # 4.5: Making Colormap
    print("\nCreating Colormap...")
    mapfolder = f'{rootdir}\\map_folder'
    if os.path.isdir(mapfolder):
        shutil.rmtree(mapfolder)
        os.mkdir(mapfolder)
    else:
        os.mkdir(mapfolder)
    for tpr in tpr_vals:
        for dp in dp_vals:
            #print('\n\n')
            desired_data = []
            for entry in updated_data:
                #print(entry)
                if entry['Ground-State'] == 1 and entry[tpr_key] == tpr and entry[dp_key] == dp:
                    mapfoldtpr = f'{mapfolder}\\tpr={tpr}'
                    mapfolderdp = f'{mapfoldtpr}\\doping{dp}'
                    if not os.path.isdir(mapfoldtpr):
                        os.mkdir(mapfoldtpr)
                    if not os.path.isdir(mapfolderdp):
                        os.mkdir(mapfolderdp)
                    desired_data.append(entry)
            if not desired_data:
                pass
            else:
                df.make_map(desired_data, tpr, dp, g_vals, gpr_vals)
    print('Figure Creation Complete')



if upload:
    print("\nUploading Data...")
    # 4:  Put the database into a cloud based engine that could handle it
    # Connecting to the MongoDB cloud
    #   Choosing the cluster that we will be using in the cloud and the database info
    # Below commented out is the ability to upload to the mongo cloud. In case one would want to do that.
    # connect_info = 'mongodb+srv://mtm9:Tunafish1!@cluster0.oorm7.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
    connect_info = 'mongodb+srv://mtm9:Tunafish1!@cluster0.oorm7.mongodb.net/test?authSource=admin&replicaSet=atlas-5f1qza-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true'
    db_name = 'WangLab'
    col_name = 'NGSED_specific_2D'

    # Getting access to the database with the connection info
    # cloud_data = df.clean_mongo_cloud(connect_info, db_name, col_name)
    local_data = df.clean_mongo_local(db_name, col_name)

    # Setting up the database and imputing the data
    # df.clean_and_insert(cloud_data, updated_data)
    df.clean_and_insert(local_data, updated_data)

    print("Uploading Complete")

print("Program Finished")