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
#outputted data from a nitto seiko driver and to reformatit.
#The original torque and encoder values are taken, transformed, recaluclated
#using a predetermined conversion factor then formatted to me the ASG standard.
#-----------------------------------------------------------------------------
#*****************************************************************************

import csv
import os

# Function to read values from CSV
#Lines 17 & 20 will be the only lines we look at, this should be the lines
#containing all Torque and Encoder values
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
            # Exit loop early if both rows are found
            if encoder_data and torque_data and len(encoder_data) == 10001 and len(torque_data) == 10001:
                return encoder_data, torque_data
            

# Function to reverse list
def reverse_list(lst):
    return lst[::-1]

# Function to calculate final torque with a given scaling factor
def calculate_final_torque(torque_list, scaling_factor):
    return [(float(torque) * scaling_factor) if torque else 0 for torque in torque_list]

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
    # Filter out empty strings and convert to int lists
    encoder_array = convert_to_int_list(encoder_array) 
    torque_array = convert_to_int_list(torque_array)
    torque_array = nullify_torque_outliers(torque_array)#STEP 4
    encoder_array = calculate_compounded_angle(encoder_array)#STEP 5
    torque_array = calculate_final_torque(torque_array, scaling_factor) #STEP 6
    create_csv(torque_array, encoder_array, output_file_path) #STEP 7

# Main function for initialization
def main():

    print("*_______________________________________________*")
    base_input_dir = input("Enter the base input directory (e.g., C:\\Users\\user\\file\\Input_Torque_File): ").strip()

    subdirectories = [d for d in os.listdir(base_input_dir) if os.path.isdir(os.path.join(base_input_dir, d))]
    print("******************************")
    print("Found Sub-Directories:")
    for y in range(len(subdirectories)):
        print(f"{y+1}. {subdirectories[y]}")
    print("******************************")
    print()

    scaling_factors_input = input("Enter Scaling factors for each station separated by commas in order from the subdirectory list above: ").split(',')

    # Get all subdirectories in the base input directory

    if len(subdirectories) != len(scaling_factors_input):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Error: The number of subdirectories must match the number of scaling factors")
        print("1. Ensure the correct number of scaling factors have been inputted\n2. Delete any unescessary files in folder")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print()

        return
    for subdirectory, scaling_factor in zip(subdirectories, scaling_factors_input):
        scaling_factor = float(scaling_factor.strip())
        input_dir = os.path.join(base_input_dir, subdirectory)
        output_dir = os.path.join(base_input_dir, f'New_{subdirectory}_Torque_Study')
        os.makedirs(output_dir, exist_ok=True)

        try:
            # Get all CSV files in the current subdirectory
            csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]

            if len(csv_files) < 30:
                print(f"Error: Subdirectory {subdirectory} does not contain at least 30 CSV files.")
                continue

            # Process files after validation
            print()
            print(f"Proscessing Folder...")
            for i, input_file in enumerate(csv_files[:30]):
                input_file_path = os.path.join(input_dir, input_file)
                output_file_path = os.path.join(output_dir, f'{subdirectory}_TORQUE_CSV_{i + 1}.csv')
                process_file(input_file_path, output_file_path, scaling_factor)
                print(f'Processed {input_file_path} and saved to {output_file_path}')
            print(f"File formating complete for subdirectory {subdirectory}")
        except Exception as e:
            print(f"Error: {e}")
            print("There was an error with the file paths or processing. Please restart and enter the correct information.")
            return

if __name__ == "__main__":
    main()
