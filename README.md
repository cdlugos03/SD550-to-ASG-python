# SD550-to-ASG-python
The Purpose of this program is to provide an efficent way to convert formatted test data from a Nitto Seiko SD550 Driver to an ASG driver format. The Nitto Seiko output data contains the .NWD filetype which has a similar structure to a .CSV

This is an example of the Nitto Seikos file output for a seat to strip study![image](https://github.com/user-attachments/assets/32ac9b26-805b-4a68-8cf7-d2e05d769cd0)
compared to an ASG output as a CSV ![image](https://github.com/user-attachments/assets/90e01517-0087-4a5f-afa2-a0623bcc06e2)

The majority of the file is made up of the Torque and Encoder data recorded throughout the test. The rest of the information above is negligble for the conversion. This program will only scan lines 18 & 21 (indexed at 17 & 20) which will both be converted to torque (n-m) and angle (deg) through the use of test conversion factors and encoder resolution. 

## Program Details 
This program can be broken down into 3 orders of operation: **User Input, Test Data Processing/Formating, and File Output** 
Using CSV and OS libraries in python we are able to convert the NWD (output from SD550) to a readable CSV for the seat to strip excel program to calculate prescribed limits. 

### User Input
The starting point of the program is below the `main` function. The user will be prompted to input a file path to a folder that contains the seat to strip data per station seperated in folders. The program will begin to scan the contents of the file path and print the sub-directories for the user. After this process is finished the program will prompt for the input of the custom scaling factors per station. These values can be found by following the steps in the SD550 to ASG Format Conversion Setup Guide Slideshow. 
### Data Processing
The bulk of the program runtime is spent processing, calculating, and reformatting the data in sequential steps. The first step is validating the contents of the subdirectories by checking file type and the number of files within each folder. If there are files with anything other than an .nwd basename they will be skipped. The number of NWD files in the subdirectory is tabulated and checked if it is above 30, if not the program throws an error.

After Validation we move into Proccessing the actual files. After the input file path and output file path have been determined we pass those along with our scaling factors to the function `process_file` which is where the data is manipulated. The process of steps in the proper conversion are as follows: Read .nwd files, reverse the order of both data entries (torque and encoder), delete every other entry of data so the tick time is in 1ms intervals rather than 0.5ms, convert the list to integers, nullify any outliers or anomolies, calculate the compunded angle, and finally calculating the final torque given the scaling factor. This is a simplified version of the series of steps it takes to successfully do this, however it gives a good introduction to understanding the series of steps that have been taken. 

### File Output
The Final step in this program is taking the converted csv file, formatting it to the ASG driver output. The function `creat_csv` is mainly responsible for this process. The torque data, angle data, and output file path are passed through this function to be written and saved as a CSV. The output directory was created and determined by the parent directory of the Inputted file directory from the beggining. 
