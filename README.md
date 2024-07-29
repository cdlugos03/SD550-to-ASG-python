# SD550-to-ASG-python
The Purpose of this program is to provide an efficent way to convert formatted test data from a Nitto Seiko SD550 Driver to an ASG driver format. The Nitto Seiko output data contains the .NWD filetype which has a similar structure to a .CSV ![image](https://github.com/user-attachments/assets/32ac9b26-805b-4a68-8cf7-d2e05d769cd0)
The majority of the file is made up of the Torque and Encoder data recorded throughout the test. The rest of the information above is negligble for the conversion. This program will only scan lines 18 & 21 (indexed at 17 & 20) which will both be converted to torque (n-m) and angle (deg) through the use of test conversion factors and encoder resolution. 

The libraries used in this program are limited to csv and os which should both be acessible locally. 
