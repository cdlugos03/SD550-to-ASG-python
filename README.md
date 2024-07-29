# SD550-to-ASG-python
The Purpose of this program is to provide an efficent way to convert formatted test data from a Nitto Seiko SD550 Driver to an ASG driver format. The Nitto Seiko output data contains the .NWD filetype which has a similar structure to a .CSV

This is an example of the Nitto Seikos file output for a seat to strip study![image](https://github.com/user-attachments/assets/32ac9b26-805b-4a68-8cf7-d2e05d769cd0)
compared to an ASG output as a CSV ![image](https://github.com/user-attachments/assets/90e01517-0087-4a5f-afa2-a0623bcc06e2)

The majority of the file is made up of the Torque and Encoder data recorded throughout the test. The rest of the information above is negligble for the conversion. This program will only scan lines 18 & 21 (indexed at 17 & 20) which will both be converted to torque (n-m) and angle (deg) through the use of test conversion factors and encoder resolution. 

The libraries used in this program are limited to csv and os which should both be acessible locally. 
## Program Details 
This program can be broken down into 3 orders of operation: **User Input, Test Data Processing/Formating, and File Output** 
Using CSV and OS libraries in python we are able to convert the NWD (output from SD550) to a readable CSV for our excel program to calculate prescribed limits. 
