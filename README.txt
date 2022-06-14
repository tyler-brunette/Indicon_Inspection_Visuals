Updated 06/13/2022

General:
When using the software, be sure that you put the json files containing the shape data for still images and live images in the same folder
as the programs as well as the static image(s).
This program was developed using Python 3.10.4 and Pygame 2.1.2.
Functionality of the software cannot be guaranteed in any version prior to these.

Indicon_Inspection_Visuals.py:
TODO comments have been used to direct the user through setup of the program.
In order to receive a TCP message, you must set the host and port variables to the device's IP address that the program is running on and the desired port.
The computer sending the message (the client) must direct the message to this IP address and port.
In order for the program to get inspection data, you must update the global directory variable to the path of the Windows share (where the json files and images are stored).
When setting up the program, be sure to change the static image files located in the main() method to the desired images.

Shape_Setup.py:
TODO comments have been used to direct the user through setup of the program.
In order for the program to support live image shape data, you must update the global directory variable to the path containing the live images.
To properly save the data to a file, use a json file formatted as shown below:
{
	"Shapes": [
	]
}

Before launching the program, change the value of the output_file variables located in the gui() method to the files you wish to save to.
You should have two json files that you save shape data to. One used for static image shapes and one used for live image shapes.
Before using the program, change the values of the image_file variable located in the "match image_text:" statement in the gui() method to the desired static image files.