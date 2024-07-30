#           :::::::::::::         :::::::::::::                       ::::::::::::                                                      
#           :::::::::::::         ::::::::::::                        ::::::::::::                                                      
#           :::::::::::::        ::::::::::::                         ::::::::::::                                                      
#           :::::::::::::        :::::::::::                          :::::::::::                                                       
#           :::::::::::::       ::::::::::::                         ::::::::::::            :::::                       :::::          
#           :::::::::::::       :::::::::::    ::::::::::::::::::::: ::::::::::::      :::::::::::::::::           :::::::::::::::::    
#            ::::::::::::      :::::::::::  :::::::::::::::::::::::  ::::::::::::   :::::::::::::::::::::       ::::::::::::::::::::::: 
#            ::::::::::::     :::::::::::  ::::::::::::::::::::::::  :::::::::::   ::::::::::::::::::::::::    :::::::::::::::::::::::::
#            ::::::::::::    ::::::::::::::::::::::::: :::::::::::: ::::::::::::  :::::::::::   :::::::::::  :::::::::::::  ::::::::::::
#            ::::::::::::    :::::::::::::::::::::::   :::::::::::: :::::::::::: ::::::::::::    ::::::::::: ::::::::::::    :::::::::::
#            :::::::::::::  :::::::::::::::::::::::    :::::::::::  :::::::::::: :::::::::::::::::::::::::::::::::::::::     :::::::::::
#            ::::::::::::: ::::::::::: ::::::::::::    :::::::::::  ::::::::::: ::::::::::::::::::::::::::: ::::::::::::     :::::::::::
#             :::::::::::::::::::::::  ::::::::::::   :::::::::::: :::::::::::: ::::::::::::::::::::::::::: ::::::::::::     :::::::::::
#             ::::::::::::::::::::::  ::::::::::::    :::::::::::: :::::::::::: ::::::::::::::::::::::::::::::::::::::::    ::::::::::::
#              ::::::::::::::::::::   ::::::::::::    :::::::::::  :::::::::::: ::::::::::::               :::::::::::::    ::::::::::::
#              :::::::::::::::::::    :::::::::::::   :::::::::::  :::::::::::  :::::::::::::          :   :::::::::::::    ::::::::::: 
#              ::::::::::::::::::     ::::::::::::::::::::::::::: ::::::::::::  :::::::::::::::::::::::::   ::::::::::::   :::::::::::: 
#               ::::::::::::::::       :::::::::::::::::::::::::: ::::::::::::   :::::::::::::::::::::::    ::::::::::::::::::::::::::  
#               :::::::::::::::        :::::::::::::::::::::::::  ::::::::::::    ::::::::::::::::::::::     ::::::::::::::::::::::::   
#----            :::::::::::::           :::::::::::: ::::::::::  :::::::::::        :::::::::::::::::::       :::::::::::::::::::      
# =---==                                      :                                                                     ::::::::::          
#   -------                                                                                                                             
#     ------=                                         -----------------------------------====------------------===-----------------=    
#      --------                      =--------------------------------------------------------------==                                  
#       -------==       ==-------------------------------------------------                                                             
#         -------------------------------------------------=                                                                            
#          --------------------------------------                                                                                       
#           =---------------------------                                                                                                
#            -------------------                                                                                                        
#            -------------                                                                                                              
#             ------                                                                                                                    

#*****************************************************************************
#----------------------------------------------------------------------------
#Date: 7/17/2024
#Author: Cooper Dlugos (cooper.dlugos@valeo.com)
#Project name: SD550 to ASG Format Conversion

#Description: The purpose of this program is to take 
#output data from a nitto seiko driver and to reformat it.
#The original torque and encoder values are taken, transformed, recaluclated
#using a predetermined conversion factor based on each study then formatted to 
# a similar ASG format standard.
#-----------------------------------------------------------------------------
#*****************************************************************************

import csv
import os

# Function to read values from CSV
def read_values(file_path):
    with open(file_path, newline='', encoding="utf8", errors='replace') as fd:
        reader = csv.reader(fd)
        encoder_data = None
        torque_data = None
        for idx, row in enumerate(reader):
            if idx == 17:
                torque_data = row
            elif idx == 20:
                encoder_data = row
            if encoder_data and torque_data and len(encoder_data) == 10001 and len(torque_data) == 10001:
                return encoder_data, torque_data

# Function to reverse list
def reverse_list(lst):
    return lst[::-1]

# Function to calculate final torque with a given scaling factor
def calculate_final_torque(torque_list, scaling_factor):
    return [((torque) * scaling_factor) if torque else 0 for torque in torque_list]

# Function to convert list of strings to list of ints
def convert_to_int_list(str_list):
    return [int(item) for item in str_list if item]

# Function to calculate compounded angle
def calculate_compounded_angle(angle_list):
    final_angle_list = []
    revolutions = 0
    previous_angle = 0
    tolerance = 10  # Define a tolerance level for detecting revolutions
    
    for i in range(len(angle_list)):
        current_angle = ((angle_list[i] * 360) / 4095)
        
        if i > 0 and (previous_angle - current_angle) > tolerance:
            revolutions += 1

        total_degrees_rotated = revolutions * 360
        compounded_angle = current_angle + total_degrees_rotated
        final_angle_list.append(round(compounded_angle, 4))
        previous_angle = current_angle
    
    return final_angle_list

# Function to create CSV file with torque and angle data
def create_csv(torque_list, angle_list, output_file_path):
    with open(output_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Task', 'Bolt', 'Sequence Step', 'Time (ms)', 'Prevail Torque', 'Torque',
                         'Torque Units', 'Angle Total (deg)', 'Angle since Threshold Torque (deg)'])
        for i, (torque, angle) in enumerate(zip(torque_list, angle_list), start=1):
            writer.writerow([1, 1, 1, i, 0, torque, 'n-m', angle, angle])

def find_max_torque(torque_list):
    max_val = torque_list[0]
    for i in range (len(torque_list)):
        if max_val <= torque_list[i] and torque_list[i] < 7000:
            max_val = torque_list[i]
        else:
            continue
        
    return max_val

# Function to nullify torque outliers (anything with a torque value over 7000 will be written as a 0)
def nullify_torque_outliers(torque_list):
    nullified_values = 0
    for i in range(len(torque_list)):
        if torque_list[i] >= 7000:
            torque_list[i] = 0
            nullified_values += 1 
    print("Nullified values: ", nullified_values)
    return torque_list

# Function to process the file and convert formats
def process_file(file_path, output_file_path, scaling_factor):
    vals = read_values(file_path) #STEP 1
    encoder_array = vals[0]
    torque_array = vals[1]
    encoder_array = reverse_list(encoder_array)  # STEP 2
    torque_array = reverse_list(torque_array)
    encoder_array = encoder_array[::2]  # STEP 3
    torque_array = torque_array[::2]
    torque_array.pop(0)
    encoder_array.pop(0)
    encoder_array = convert_to_int_list(encoder_array) 
    torque_array = convert_to_int_list(torque_array)
    torque_array = nullify_torque_outliers(torque_array)#STEP 4
    encoder_array = calculate_compounded_angle(encoder_array)#STEP 5
    torque_array = calculate_final_torque(torque_array, scaling_factor) #STEP 6
    create_csv(torque_array, encoder_array, output_file_path) #STEP 7
    print(f"Max value for this study is: {find_max_torque(torque_array)}")

# Function to extract the parent directory of the input path
def extract_parent_directory(input_path):
    parent_directory = os.path.dirname(input_path)
    return parent_directory

# Main function for initialization
def main():
    print("________________________________________________________________________________________________")
    base_input_dir = input("Enter the base input directory (e.g., C:\\Users\\user\\file\\Input_Torque_File): ").strip()

    try:
        subdirectories = [d for d in os.listdir(base_input_dir) if os.path.isdir(os.path.join(base_input_dir, d))]
        print("******************************")
        print("Found Sub-Directories:")
        for y in range(len(subdirectories)):
            print(f"{y+1}. {subdirectories[y]}")
        print("******************************")
        print()

    except Exception as e:
        print(f"No Sub Directories Found: {e}")
        return

    scaling_factors_input = input("Enter Scaling factors for each station separated by commas in order from the subdirectory list above: ").split(',')

    if len(subdirectories) != len(scaling_factors_input):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Error: The number of subdirectories must match the number of scaling factors")
        print("1. Ensure the correct number of scaling factors have been inputted\n2. Delete any unnecessary files located in the input files folder")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print()
        return

    parent_directory = extract_parent_directory(base_input_dir)

    for subdirectory, scaling_factor in zip(subdirectories, scaling_factors_input):
        scaling_factor = float(scaling_factor.strip())
        input_dir = os.path.join(base_input_dir, subdirectory)

        try:
            output_dir = os.path.join(parent_directory, f'Output\ASG_Formatted_{subdirectory}_Torque_Study')
            os.makedirs(output_dir, exist_ok=True)

            # Get all NWD files in the current subdirectory
            nwd_files = [f for f in os.listdir(input_dir) if f.endswith('.nwd')]

            if len(nwd_files) < 30:
                print(f"Error: Subdirectory {subdirectory} does not contain at least 30 NWD files.")
                continue

            # Process files after validation
            print()
            print(f"Processing Folder...")
            for i, input_file in enumerate(nwd_files[:30]):
                input_file_path = os.path.join(input_dir, input_file)
                output_file_path = os.path.join(output_dir, f'{subdirectory}_TORQUE_CSV_{i + 1}.csv')
                process_file(input_file_path, output_file_path, scaling_factor)
                print(f'Processed {input_file_path} and saved to {output_file_path}')
            print(f"File formatting complete for subdirectory {subdirectory}")
        except Exception as e:
            print(f"Error: {e}")
            print("There was an error with the file paths or processing. Please restart and enter the correct information.")
            return

if __name__ == "__main__":
    main()
