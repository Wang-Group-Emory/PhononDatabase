'''
Matt Myers
02/04/2022
Senior Thesis
Data Adjustment Functions

This Program is a list of functions used in the creation
of the databse. Updated for the specfic purpose of running
then new data
'''
# Importing libraries
from options import *
import win32api, os, getpass, re, certifi
from pathlib import Path
from collections import OrderedDict
from pymongo import MongoClient
import numpy as np
from operator import itemgetter
import matplotlib.image as img
import json
import os
from fpdf import FPDF
import shutil
import matplotlib.pyplot as plt

def find_and_set_directory():
    # Finding the drives on the computer
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    path_found = False

    # Finding username on computer
    current_user_name = getpass.getuser()

    # Finding the path for the directory "NGSED"
    for drive in drives:
        if path_found:
            break
        elif path_found:
            continue
        
        # This goes through the most common drive first to save time
        if drive == 'C:\\' and not path_found:
            start = drive + 'Users\\' + current_user_name+ '\\'
            for dirpath, dirnames, filenames in os.walk(start):
                for dirname in dirnames:
                    if dirname == "NGSED":
                        NGpath = os.path.join(dirpath, dirname)
                        path_found = True
                        break
                else:
                    continue
                break
        # Otherwise it loops through the rest of the drives
        elif not path_found:
            start = drive
            print("Folder in " + start + "Drive")
            for dirpath, dirnames, filenames in os.walk(start):
                for dirname in dirnames:
                    if dirname == "NGSED":
                        NGpath = os.path.join(dirpath, dirname)
                        print("Folder Path: "+ NGpath)
                        path_found = True
                        break
                else:
                    continue
                break
    #Seting the working directory to the correct path
    os.chdir(NGpath)

def dir_path_find(nfiles, blacklist, addfiles):
    count = 0
    want_paths = []
    # Getting the starting path and checking
    path = Path(os.getcwd())
    
    # Looping through the files and folders to find the desired files
    for root, dirs, files in os.walk(path):
        # if '\\Hubbard_02-16-2022' in root:
        #     print(root)
        for file in files:
            if file in nfiles and (all((i in files for i in nfiles)) or all((i in files for i in addfiles))) and not any(x in root for x in blacklist):
                want_paths.append(root)
                count += 1
                break
        else:
            continue
    
    return(want_paths)

def convert_to_float(lsts):
    # looping through each element
    for x in range(len(lsts)):
        # Converting each element into float
        #print(lsts[x])
        lsts[x] = float(lsts[x])

def fancy_prime(x):
    # Converting the differnt options both into '
    options = ['pri','pr']
    rep = '\''
    newx = re.sub("|".join(sorted(options, key = len, reverse = True)), rep, x)
    return(newx)

def revpath(path):
    reversed_string = "\\".join(path.split("\\")[::-1])
    return(reversed_string)

def get_gs(path, primecount):
    # Converts the path into ' for consistnecy
    path = fancy_prime(path)
    path = revpath(path)
    g_dict = {}
    # Start searching for g then add ' each time
    gcount = 'g'
    # Will continue until desired derivative reached
    while(gcount != "g"+("\'"*(primecount+1))):
        gupdate = {}
        # If it is in path it will save the number
        if gcount in path:
            g_num = []
            next_letter_g = path.find('_'+gcount)+len('_'+gcount)
            while path[next_letter_g] != '_':
                if next_letter_g != path[-1]:
                    g_num.append(path[next_letter_g])
                    next_letter_g += 1
                else:
                    g_num.append(path[next_letter_g])
                    break
            g_num = ''.join(g_num)
            gupdate = {gcount: float(g_num)}
            g_dict.update(gupdate)
        # If not in path setting it equal to zero
        else:
            gupdate = {gcount: float(0)}
            g_dict.update(gupdate)
        gcount += '\''
    return(g_dict)

def get_path_data(path):
    # First getting doping information
    if 'doping' in path:
        doping_num = path[path.find('doping')+len('doping')]
        doping_num = []
        next_letter_doping = path.find('doping')+len('doping')
        while path[next_letter_doping] != 'h':
            doping_num.append(path[next_letter_doping])
            next_letter_doping += 1
        doping_num = ''.join(doping_num)
    elif 'Doping' in path:
        doping_num = path[path.find('Doping')+len('Doping')]
        doping_num = []
        next_letter_doping = path.find('Doping')+len('Doping')
        while path[next_letter_doping] != 'h':
            doping_num.append(path[next_letter_doping])
            next_letter_doping += 1
        doping_num = ''.join(doping_num)
    elif 'half-filling' in path:
        doping_num = 0
    if 'k=' in path:
        k_num = []
        next_letter_k = path.find('k=')+len('k=')
        while path[next_letter_k] != '\\':
            k_num.append(path[next_letter_k])
            next_letter_k += 1
        k_num = ''.join(k_num)
    elif 'momentum' in path:
        k_num = []
        next_letter_k = path.find('momentum')+len('momentum')
        while path[next_letter_k] != '\\':
            k_num.append(path[next_letter_k])
            next_letter_k += 1
        k_num = ''.join(k_num)
    if 'tpr' in path:
        tpr_num = []
        temp_path = revpath(path)
        if 'tpr=' in temp_path:
            next_letter_tpr = temp_path.find('tpr=')+len('tpr=')
        elif 'tpr' in temp_path:
            next_letter_tpr = temp_path.find('tpr')+len('tpr')
        while temp_path[next_letter_tpr] not in ['\\','_']:
            tpr_num.append(temp_path[next_letter_tpr])
            next_letter_tpr += 1
        tpr_num = ''.join(tpr_num)
    if 'resU' in path:
        u_num = []
        next_letter_u = path.find('resU')+len('resU')
        while path[next_letter_u] != '_':
            u_num.append(path[next_letter_u])
            next_letter_u += 1
        u_num = ''.join(u_num)
    if ('_W') in path:
        temp_path = revpath(path)
        if '\\' not in temp_path.partition('_W')[2]:
            w_num = temp_path.partition('_W')[2]
        elif '_W' in temp_path:
            w_num = []
            next_letter_w = temp_path.find('_W')+len('_W')
            while temp_path[next_letter_w] != '\\':
                w_num.append(temp_path[next_letter_w])
                next_letter_w += 1
            w_num = ''.join(w_num)
    # Getting g and prime data
    gs = get_gs(path,3)
    if 'k_num' in locals():
        dict_data = {'Doping (h)': float(doping_num), 'K': float(k_num), 't\'':float(tpr_num), 'Res (U)': float(u_num), 'Freq (W)': float(w_num)}
    else:
        dict_data = {'Doping (h)': float(doping_num), 't\'':float(tpr_num), 'Res (U)': float(u_num), 'Freq (W)': float(w_num)}
    return(dict(dict_data, **gs))

def get_last_line(file, name):
    if len(file) > 1:
        for x in range(len(file)-1,-1,-1):
            temp_line = file[x]
            #print(temp_line)
            temp_line_split = list(filter(None, re.split(r'\t+',temp_line.replace(' ','\t').rstrip('\n'))))
            #print(temp_line_split)
            ##### MOST FILES HAVE LENGTH 32, 51, OR 99. ONLY ABOUT 5 DONT, 68,69
            if len(temp_line_split) in [32,51,99]:
                last_line = temp_line_split
                return(last_line)
    elif file == None or len(file) == 0:
        if name == "var":
            return(fill_nan_small(file, 32))
        elif name == "gauss":
            return(fill_nan_small(file, 99))
    else:
        temp_line = file[0]
        #print(temp_line)
        temp_line_split = list(filter(None, re.split(r'\t+',temp_line.replace(' ','\t').rstrip('\n'))))
        #print(temp_line_split)
        ##### MOST FILES HAVE LENGTH 32, 51, OR 99. ONLY ABOUT 5 DONT, 68,69
        if len(temp_line_split) in [32,51,99]:
            last_line = temp_line_split
            return(last_line)

def fill_nan_small(lis, length):
    lis = np.empty(length)
    lis[:] = np.nan
    return(lis)

def fill_nan(g, v, hg, hv):
    # Filling a list with nothing but NA if no information
    lg = len(hg)
    lv = len(hv)
    if g == None:
        g = np.empty(lg)
        g[:] = np.nan
    if v == None:
        v = np.empty(lv)
        v[:] = np.nan
    return(g,v)

def get_date(log):
    # Selecting the phrase before the date
    look_for = '\tStart at '
    # Searching each line for the phrase
    for line in range(len(log)):
        # When the phrase is found save the date information
        if look_for in log[line]:
            date_line = log[line]
            date = date_line.partition(look_for)[2].rstrip('\n')
            return(date)

def get_dim_and_size(log):
    # Getting the dimension and size from myLog
    # Searching for these specific phrases
    look_for = '\tRequested '
    look_for_dim = '\tRequested '
    look_for_size = '-site '
    # Looping through each line to find the phrases
    for line in range(len(log)):
        # If it matches either phrase save the information after
        if look_for in log[line]:
            data_line = log[line]
            dim_end = data_line.partition(look_for_dim)[2]
            size_end = data_line.partition(look_for_size)[2]
            size = dim_end.partition(look_for_size)[0]
            dim = size_end.partition('D')[0]
            return(float(dim), float(size))

def make_1d(a):
    # Making a 2d array 1d to search it
    new_arr = []
    for i in a:
        try:
            for j in i:
                new_arr.append(j)
        except:
            new_arr.append(i)
    return(new_arr)

def index_2d(myList, v):
    # Keeping track of the indices to get the index we want
    for i, x in enumerate(myList):
        if v in x:
            return ([i, x.index(v)])

def insert_key_value(a_dict, key, pos_key, value):
    # Inserting a value into a specific spot of dictionary
    new_dict = OrderedDict()
    for k, v in a_dict.items():
        if k==pos_key:
            new_dict[key] = value
        new_dict[k] = v
    return new_dict

def get_ground_state_old(all_data):
    lowest_data = [[all_data[0]['K'], all_data[0]['E'], all_data[0]['Short Path']]]
    # Going through all dictionaries and finding lowest energy for each k
    for data in all_data:
        e = data['E']
        if data['K'] in make_1d(lowest_data):
            two_index = index_2d(lowest_data, data['K'])
            k_index = two_index[0]
            if e < lowest_data[k_index][1]:
                lowest_data[k_index] = [data['K'], e, data['Short Path']]
        else:
            lowest_data.append([data['K'], e, data['Short Path']])
    low_paths = list(zip(*lowest_data))[2]
    full_data = []
    # Having found the paths adding a 1 for ground state and 0 otherwise
    for dataNew in all_data:
        if dataNew['Short Path'] in low_paths:
            full_data.append(insert_key_value(dataNew, 'Ground-State',  "t\'", 1))
        else:
            full_data.append(insert_key_value(dataNew, 'Ground-State',  "t\'", 0))
    return(full_data)

def get_final_dir(path):
    revpath = path[::-1]
    #print(revpath)
    rev_s_path = [revpath[0]]
    next_letter = 1
    while path[next_letter] != '\\':
        rev_s_path.append(path[next_letter])
        next_letter += 1
    rev_final_temp = ''.join(rev_s_path)
    rev_final = rev_final_temp[::-1]
    #print(rev_final)
    return(rev_final)

def remove_dupe_dicts(l):
    list_of_strings = [json.dumps(d, sort_keys=False) for d in l]
    list_of_strings = set(list_of_strings)
    return [json.loads(s) for s in list_of_strings]

def get_ground_state(all_data):
    # Getting the unique parameters without the k
    whitelist = ['Res (U)', 'g', 'g\'', 'Freq (W)', 't\'','Doping (h)']
    whitelist_info = ['Res (U)', 'g', 'g\'', 'Freq (W)', 't\'','Doping (h)', 'K', 'E']
    new_data = all_data
    k_data = all_data
    single_data = []
    ground_list = []
    lowest_paths = []
    big_list = []
    for data in new_data:
        new_data = {key:val for key,val in data.items() if key in whitelist}
        if new_data not in single_data:
            single_data.append(new_data)
    # Organizing the data into sets of parameters
    for datas in single_data:
        triplet = []
        for datal in k_data:
            adjust_datal = {key:val for key,val in datal.items() if key in whitelist}
            if datas == adjust_datal:
                unique = {key:val for key,val in datal.items() if key in whitelist_info}
                triplet.append(unique)
        big_list.append(triplet)
    # Finding lowest energy for momentum
    for sublist in big_list:
        ground_sorted = sorted(sublist, key = itemgetter('E'))
        ground_list.append(ground_sorted[0])
    # Finding the path to these ground-states
    for datak in k_data:
        for ground in ground_list:
            compdata = {key:val for key,val in datak.items() if key in whitelist_info}
            if compdata == ground:
                lowest_paths.append(datak['Short Path'])
    # Adjusting the value of ground-state to either 1 or 0
    full_data = []
    # Having found the paths adding a 1 for ground state and 0 otherwise
    for dataNew in all_data:
        if dataNew['Short Path'] in lowest_paths:
            full_data.append(insert_key_value(dataNew, 'Ground-State',  "t\'", 1))
        else:
            full_data.append(insert_key_value(dataNew, 'Ground-State',  "t\'", 0))
    return(full_data)

def make_dict_from_data(path):
    file_paths = []
    
    # Finding the file paths
    for root, dirs, files in os.walk(path):
        for file in files:
            file_paths.append(os.path.join(root,file))
    
    # For each file path it takes the data from each relevant file
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            if os.path.basename(file_path) in ['varState.txt', 'NGSED_iteration_variables.txt']:
                file_contents_vars = f.readlines()
                file_contents_var = get_last_line(file_contents_vars, "var")
                convert_to_float(file_contents_var)
            elif os.path.basename(file_path) in ['observableList.txt', 'observable_name_list.txt']:
                file_contents_obs = re.split(r'\t+',f.readline().rstrip('\n'))
            elif os.path.basename(file_path) == 'nonGaussED_eq_observables.txt':
                file_contents_gausss = f.readlines()
                file_contents_gauss = get_last_line(file_contents_gausss, "gauss")
                if np.nan in file_contents_gauss:
                    #print(f"\n Empty Gauss Observables: {file_path}")
                    pass
                else:
                    convert_to_float(file_contents_gauss)
            elif os.path.basename(file_path) == 'mylog':
                file_contents_log = f.readlines()
                file_date = get_date(file_contents_log)
                file_dim, file_size = get_dim_and_size(file_contents_log)
    
    # Creating the header elements not included
    header_elems_to_add_end1 = []
    header_elems_to_add_end2 = []
    for x in range(16):
        header_elems_to_add_end1.append('G('+ str(x)+')')
        header_elems_to_add_end2.append('L('+ str(x)+')')
    header_elems_to_add_end = header_elems_to_add_end1 + header_elems_to_add_end2
    header_elems_to_add_begin = ['E', 'Ee', 'Eph']
    
    # Combing the data and header information to create a complete set
    if len(file_contents_gauss) == 99:
        file_contents_header = header_elems_to_add_begin + file_contents_obs + header_elems_to_add_end
        file_contents_data = file_contents_gauss
    else:
        file_contents_header = header_elems_to_add_begin + file_contents_obs + header_elems_to_add_end
        file_contents_gauss, file_contents_var = fill_nan(file_contents_gauss,file_contents_var,header_elems_to_add_begin + file_contents_obs,header_elems_to_add_end)
        file_contents_data = np.append(file_contents_gauss, file_contents_var)
    file_dict = dict(zip(file_contents_header, file_contents_data))
    
    # Data being converted into a dictionary
    #short_path = path[path.find(get_final_dir(path))+len(get_final_dir(path)):]   
    short_path = path[path.find('\\All_data')+len('\\All_data'):]   
    data1 = {"Full Path": path, "Date": file_date, "Short Path": short_path}
    #add_data = {'Dimension': file_dim, 'Size': file_size, 't\'': 0}
    add_data = {'Dimension': file_dim, 'Size': file_size}
    path_data = get_path_data(root)
    return(dict(list(data1.items()) + list(add_data.items()) + list(path_data.items())  + list(file_dict.items())))

def get_key_options(dkey, data):
    options_raw = []
    for item in data:
        if item[dkey] not in options_raw:
            options_raw.append(item[dkey])
    options = sorted(options_raw, key = lambda x:float(x))
    return(options)

def make_figures(seldict, w, g, tpr, gpr):
    yarray = []
    figure_dict = {}
    site = 16
    sorted_dict = sorted(seldict, key=lambda d: d['Doping (h)'])
    startdir = os.getcwd()
    figure_folder = f'{rootdir}\\figure_folder\\w={w}\\g={g}\\gpr={gpr}\\tpr={tpr}'
    try:
        os.mkdir(figure_folder)
    except:
        pass
    os.chdir(figure_folder)
    dopingaxisx_before_division = [item['Doping (h)'] for item in sorted_dict]
    dopingaxisx = [i/site for i in dopingaxisx_before_division]
    xaxis_label = 'Doping (h) / Site (16)'
    fulldatatitle = f'w={w:.2f},g={g:.2f},g\'={gpr:.2f},t\'={tpr:.2f}-Nq(_)_vs._Doping(h)'
    all_plot = f'w={w:.2f},g={g:.2f},g\'={gpr:.2f},t\'={tpr:.2f}'
    fulldataname = f'{fulldatatitle}.eps'
    desired_quants = ['Nq(1)', 'Nq(2)', 'Nq(5)', 'Nq(10)', 'Delta[d](0)']
    for y in desired_quants:
        valueaxisy = []
        title = f'w={w:.2f},g={g:.2f},g\'={gpr:.2f},t\'={tpr:.1f}-{y}_vs._Doping(h)'
        filename = f'{title}.eps'
        valueaxisy = [item[y] for item in sorted_dict]
        yarray.append(valueaxisy)
        yaxis_label = f'{y}'
        fig1, ax1 = plt.subplots()
        ax1.plot(dopingaxisx,valueaxisy, '-o', color='#522D80')
        ax1.set_title(title)
        ax1.set_xlabel(xaxis_label)
        ax1.set_ylabel(yaxis_label)
        fig1.savefig(filename, format='eps')
        filename = f'{title}.png'
        fig1.savefig(filename, format='png')
        figure_dict[title]=fig1
        plt.close(fig1)
        #print(f'\n{title}\nXaxis={dopingaxisx}\nYaxis={valueaxisy}')
    yaxis_label_full = f'Nq(_)'
    figfull, axfull = plt.subplots()
    axfull.plot(dopingaxisx,yarray[0], '-o', label = desired_quants[0])
    axfull.plot(dopingaxisx,yarray[1], '-o', label = desired_quants[1])
    axfull.plot(dopingaxisx,yarray[2], '-o', label = desired_quants[2])
    axfull.plot(dopingaxisx,yarray[3], '-o', label = desired_quants[3])
    #axfull.plot(dopingaxisx,yarray[4], '-o', label = desired_quants[4])
    axfull.set_title(fulldatatitle)
    axfull.set_xlabel(xaxis_label)
    axfull.set_ylabel(yaxis_label_full)
    axfull.legend()
    figfull.savefig(fulldataname, format='eps')
    fulldataname = f'{fulldatatitle}.png'
    figfull.savefig(fulldataname, format='png')
    figure_dict[fulldatatitle]=figfull
    plt.close(figfull)
    figure_of_figures(all_plot)
    os.chdir(startdir)

def figure_of_figures(title):
    right_offset = 99
    down_offset = 74
    col = 0
    row = 0
    pdf = FPDF(orientation='L')
    pdf.set_auto_page_break(0)
    imagelist = [i for i in os.listdir() if i.endswith('png')]
    #print(imagelist)
    pdf.add_page()
    for image in imagelist:
        if col == 3:
            col=0
            row=1
        x=right_offset*col
        y=down_offset*row
        col += 1
        pdf.image(image,x,y,99,74)
    pdf.output(f"{title}.pdf","F")
    # # print(dic)
    # nrows = 2
    # ncols = 3
    # c = 1
    # fig, axs = plt.subplots(nrows,ncols)
    # for i in dic:
    #     title = i
    #     image = dic[i]
    #     #plt.subplot(f"{nrows}{ncols}{c}")
    #     axs[0,0].imshow(image)
    #     #plt.axis('off')
    #     axs[0,0].set_title(title)
    #     c+=1
    # plt.show()
    #######
    # nrows = 2
    # ncols = 3
    # c = 1
    # pngs = os.listdir()
    # for png in pngs:
    #     if '.png' not in png:
    #         pngs.remove(png)
    # #print(pngs)
    # fig = plt.figure()
    # for png in pngs:
    #     image = img.imread(png)
    #     fig.add_subplot(nrows, ncols, c)
    #     plt.imshow(image)
    #     plt.axis('off')
    #     #plt.title(png)
    #     plt.show()
    #     c+=1
    # fig.savefig('All.png', format='png', dpi = 600)

def make_map(seldict, tpr, dp, gs, gprs):
    plot_list = []
    x = np.arange(min(gprs)-(gprs[1]/2),max(gprs)+gprs[1],gprs[1], dtype=float)
    #print(f"x: {len(x)}")
    y = np.arange(min(gs)-(gs[1]/2),max(gs)+gs[1],gs[1], dtype=float)
    #print(f"y: {len(y)}")
    startdir = os.getcwd()
    map_folder = f'{rootdir}\\map_folder\\tpr={tpr}\\doping{dp}'
    if not os.path.isdir(map_folder):
        os.mkdir(map_folder)
    os.chdir(map_folder)
    desired_quants = ['Nq(10)', 'Sq(10)', 'Nq(2)', 'Delta[d](0)', 'Delta[s](0)', 'Delta[s+](0)']
    for a in desired_quants:
        count = 0
        title = f'Doping{dp},t\'={tpr:.1f}-{a}  g{max(gs)}-g\'{max(gprs)} by {gprs[1]}'
        print(title)
        des_2d = []
        for g in gs:
            des_1d = []
            for gpr in gprs:
                    check_count = 1
                    for lis in seldict:
                        if lis['g'] == g and lis['g\''] == gpr:
                            des_1d.append(lis[a])
                            count+=1
                        elif(check_count == len(seldict)):
                            des_1d.append(np.nan)
                            count+=1
                        else:
                            check_count+=1
            des_2d.append(des_1d)
        # Actual plotting starts below
        fig, ax = plt.subplots(figsize=(16,6))
        #print(f"Num of gprs: {len(des_2d[0])}")
        #print(f"Num of gs: {len(des_2d)}")
        plot = ax.pcolormesh(x,y,des_2d, cmap='magma_r', shading='nearest')
        plot_list.append(des_2d)
        fig.colorbar(plot, orientation='horizontal')
        fig.suptitle(r"$\mathbf{%s}$"%a, fontweight="bold")
        ax.set_title(f'{title}')
        ax.set_xticks(np.arange(min(gprs),max(gprs)+gprs[1],gprs[1], dtype=float))
        ax.set_yticks(np.arange(min(gs),max(gs)+gs[1],gs[1], dtype=float))
        ax.set_xlabel('g\'')
        ax.set_ylabel('g')
        filename = f'{title}.eps'
        fig.savefig(filename, format='eps')
        filename = f'{title}.png'
        fig.savefig(filename,format='png')
        plt.close(fig)
    fig_count = 0
    fig, axs = plt.subplots(2, 3, figsize=(35,35/4))
    plt.suptitle(f'Doping{dp}, tpr={tpr}, g{max(gs)}-g\'{max(gprs)} by {gprs[1]}')
    for col in range(3):
        for row in range(2):
            ax = axs[row, col]
            pcm = ax.pcolormesh(x,y,plot_list[fig_count], shading='nearest', cmap='magma_r')
            fig.colorbar(pcm, ax=ax, orientation='horizontal')
            ax.set_title(f'{desired_quants[fig_count]}')
            ax.set_xlabel('g\'')
            ax.set_ylabel('g')
            fig_count += 1
    filename = f'Doping{dp}, tpr={tpr}, g-g\'.eps'
    fig.savefig(filename, format='eps')
    filename = f'Doping{dp}, tpr={tpr}, g-g\'.png'
    fig.savefig(filename,format='png')
    os.chdir(startdir)

def clean_and_insert(data, lst):
    # Deleting all data in collection
    if data.estimated_document_count() != 0:
        data.drop()
    # Inserting Data
    data.insert_many(lst)

def clean_mongo_cloud(cluster_info, db_name, col_name):
    cluster = MongoClient(cluster_info, tlsCafile = certifi.where())
    #  Choosing the database that we will be working with
    db = cluster[db_name]
    #  Choosing the collection that we will be working with
    data = db[col_name]
    return(data)

def clean_mongo_local(db_name, col_name):
    client = MongoClient()
    db = client[db_name]
    col = db[col_name]
    return(col)