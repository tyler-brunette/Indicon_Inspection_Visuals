# Author: Tyler Brunette
# Company: Indicon Corporation

import json
import os
import pygame
import Button
import glob
import socket
import threading


# Method: create_thread
# Purpose: creates a separate thread for the TCP socket to run on (so it doesn't interfere with the main program)
# Parameters:
#   target: Something to run on the separate thread
# Returns: N/A
def create_thread(target):
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()


HOST = '192.168.56.1'  # TODO: IP Address of the device this will be running on (ex: raspberry pi)
PORT = 12345  # TODO: Port that the TCP message will be sent/received with
connection_established = False
conn, addr = None, None

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket object using (IPV4, TCP)
sock.bind((HOST, PORT))
sock.listen(1)  # Listens for 1 connection
data = None


# Method: receive_data
# Purpose: gets the TCP message from the client
# Parameters: N/A
# Returns: N/A
def receive_data():
    global data
    try:
        while True:
            data = conn.recv(1024).decode()
    except ConnectionResetError:
        data = data
        wait_for_connection()


# Method: wait_for_connection
# Purpose: Waits for a client to connect to the program, then calls the receive_data method
# Parameters: N/A
# Returns: N/A
def wait_for_connection():
    global connection_established, conn, addr
    conn, addr = sock.accept()  # wait for a connection, program will not proceed until a connection is made
    print('Client connected')
    connection_established = True
    receive_data()


create_thread(wait_for_connection)  # Runs the TCP methods on a separate thread


global directory
directory = 'D:\\Images\\Left\\2022-05-16\\RHF122133072454630'  # TODO: Directory of the Windows share
current_directory = os.getcwd()  # Current directory of the python script


# Method: get_inspection
# Purpose: gets the data necessary to run the program
# Parameters:
#   String file_name: file name of the json file to read from
# Returns:
#   shapes_to_draw: Array of ShapeToDraw objects
def get_inspection(file_name):

    # Parse the json file and store as a dict object
    shape_file = "ShapeData.json"
    live_shape_file = "LiveImageShapes.json"
    json_file = open(file_name)
    variables = json.load(json_file)
    json_file.close()

    live_shape_json = open(live_shape_file)
    live_shape_data = json.load(live_shape_json)
    live_shape_json.close()

    shape_json = open(shape_file)
    shape_data = json.load(shape_json)
    shape_json.close()

    live_image_shapes = live_shape_data['Shapes']
    shapes = shape_data['Shapes']
    cameras = variables['Cameras']
    shapes_to_draw = []
    failed_inspections = []
    shape_count = 0
    fail_count = 0

    for camera in cameras:
        inspections = camera['Inspections']
        image_locations = camera['ImageLocations']
        for inspection in inspections:
            result_parameters = inspection['ResultParameters']
            shape_key = ""
            parameter_keys = []
            parameter_values = []
            index = 0
            for parameter in result_parameters:
                parameter_keys.insert(index, parameter[0])
                parameter_values.insert(index, parameter[1])
                index = index + 1
                if len(shape_key) == 0:
                    shape_key = parameter[1]
                else:
                    shape_key = shape_key + " " + parameter[1]

            result = inspection['Result']

            # If inspection failed, then create a FailedInspection object with the data from the inspection
            if result == 'F':
                live_image = ""
                for image in image_locations:
                    if image['StorageType'] == 'ID' and image['ImageType'] == 'Png':
                        live_image = image['FileName']
                for live_image_shape in live_image_shapes:
                    if live_image_shape['key'] == shape_key:
                        inspection_name = inspection['Name']
                        failed_inspections.insert(fail_count,
                                                  FailedInspection(parameter_keys, parameter_values,
                                                                   inspection_name, live_image, live_image_shape))

            for shape_to_draw in shapes:

                # If the keys in the result parameters match a shape's key, display the given shape
                if shape_to_draw['key'] == shape_key:
                    color = 1
                    if result == 'P':
                        color = 0
                    elif result == 'F':
                        color = 1
                    elif result == 'p':
                        color = 2
                    elif result == 'f':
                        color = 3
                    name = shape_to_draw['name']
                    shape = shape_to_draw['shape']
                    display_name = shape_to_draw['display_name']
                    x = shape_to_draw['x']
                    y = shape_to_draw['y']
                    height = shape_to_draw['height']
                    width = shape_to_draw['width']
                    key = shape_to_draw['key']
                    image = shape_to_draw['image']
                    shapes_to_draw.insert(shape_count, ShapeToDraw(name, shape, color, display_name,
                                                                   x, y, height, width, key, image))
                    shape_count = shape_count + 1

    return shapes_to_draw, failed_inspections


# Class: FailedInspection
# Purpose: Information about failed inspections to display on the GUI
# Parameters:
#   String Array keys: All keys from the result parameters for this inspection
#   String Array values: All values of the keys from the result parameters for this inspection
#   String inspection_name: Name of the inspection (from json file)
#   String image_file: File location of the live image from the inspection
#   ShapeToDraw shape_to_draw: Holds the information about the shape to be drawn on the image
# Returns: N/A
class FailedInspection:

    # Method: __init__
    # Purpose: Initializes a FailedInspection object
    # Parameters: See Above
    # Returns: N/A
    def __init__(self, keys, values, inspection_name, image_file, shape_to_draw):
        self.keys = keys
        self.values = values
        self.inspection_name = inspection_name
        self.image_file = directory + '\\' + image_file
        self.shape_to_draw = shape_to_draw

    # Method: display_image
    # Purpose: displays the live image for the inspection from the json file on the screen
    # Parameters:
    #   Surface screen: surface to draw the image on
    #   Int x: x coordinates to draw the image (left)
    #   Int y: y coordinates to draw the image (top)
    #   Float scale: scale factor of the live image
    # Returns: N/A
    def display_image(self, screen, x, y, scale):
        image = pygame.image.load(self.image_file).convert()
        live_image = Button.Button(image=image, x=x, y=y, scale=scale)
        live_image.draw(screen)

    # Method: draw_shape
    # Purpose: draws a shape on the live image
    # Parameters:
    #   Surface screen: surface to draw the shape on
    #   Int image_x: x position of the image to draw the shape on (left)
    #   Int image_y: y position of the image to draw the shape on (top)
    #   Float scale: scale factor of the image
    # Returns: N/A
    def draw_shape(self, screen, image_x, image_y, scale):
        name = self.shape_to_draw['name']
        shape = self.shape_to_draw['shape']
        color = 1
        display_name = self.shape_to_draw['display_name']
        x = self.shape_to_draw['x']
        y = self.shape_to_draw['y']
        height = self.shape_to_draw['height']
        width = self.shape_to_draw['width']
        key = self.shape_to_draw['key']
        image = self.shape_to_draw['image']
        shape_to_draw = ShapeToDraw(name, shape, color, display_name, x, y, height, width, key, image)
        shape_to_draw.draw_shape(screen, image_x, image_y, scale)

    # Method: fill_table
    # Purpose: creates a table with the result parameter information of the inspection
    # Parameters:
    #   Surface screen: surface to draw the shape on
    #   Rect table_rect: rectangle to fill the data in
    # Returns: N/A
    def fill_table(self, screen, table_rect):
        table_color = (220,220,225)  # Light gray
        dark_text_color = (20, 20, 20)  # Dark gray
        font_size = 24
        font = pygame.font.SysFont("Times New Roman", size=font_size)  # font to use for the name label

        text_x = table_rect.left + 2
        index = 0
        for key in self.keys:
            pygame.draw.rect(screen, table_color, table_rect)
            key_text = font.render(key + ':', True, dark_text_color)
            value_text = font.render(self.values[index], True, dark_text_color)
            screen.blit(key_text, (text_x, table_rect.top))
            value_x = text_x + key_text.get_width() + 8
            screen.blit(value_text, (value_x, table_rect.top))
            table_rect = pygame.Rect(table_rect.left, table_rect.bottom, table_rect.width, table_rect.height)
            index = index + 1


# Class: ShapeToDraw
# Purpose: Object of a shape to draw on the GUI
# Parameters:
#   String name: name of the inspection item being highlighted
#   Int shape: shape to draw on the screen (0 = circle, 1 = rectangle)
#   Int color: color of the shape (0 = Green, 1 = Red, 2 = Yellow, 3 = Cyan, 4 = Orange)
#   Bool display_name: chooses whether to display the name next to the shape or not
#   Int x: x position to draw the shape (center)
#   Int y: y position to draw the shape (center)
#   Int height: height of the shape
#   Int width: width of the shape
#   String shape_key: key that corresponds to the ResultParameters
#   String image: image to draw the shape on
# Returns: N/A
class ShapeToDraw:

    # Method: __init__
    # Purpose: Initializes a ShapeToDraw object
    # Parameters: See Above
    # Returns: N/A
    def __init__(self, name, shape, color, display_name, x, y, height, width, shape_key, image):
        self.name = name  # name of the inspection item being highlighted
        self.shape = shape  # shape to draw on the screen (0 = circle, 1 = rectangle)
        self.color = color  # color of the shape (0 = Green, 1 = Red, 2 = Yellow, 3 = Cyan, 4 = Orange)
        self.display_name = display_name  # chooses whether to display the name next to the shape or not
        self.x = x  # x position to draw the shape (center)
        self.y = y  # y position to draw the shape (center)
        self.height = height  # height of the shape
        self.width = width  # width of the shape
        self.shape_key = shape_key  # key that corresponds to the ResultParameters
        self.image = image  # image to draw the shape on
        self.line_width = 5  # line width of the shape

    # Method: draw_shape
    # Purpose: draws a shape on the screen
    # Parameters:
    #   Surface screen: surface to draw the shape on
    #   Int image_x: x position of the image to draw the shape on (left)
    #   Int image_y: y position of the image to draw the shape on (top)
    #   Float scale: scale factor of the image
    # Returns: N/A
    def draw_shape(self, screen, image_x, image_y, scale):

        shape_color = (255,0,0) # color of the shape (default red)

        if self.color == 0:
            shape_color = (0,255,0)  # green
        elif self.color == 1:
            shape_color = (255,0,0)  # red
        elif self.color == 2:
            shape_color = (255, 240, 31)  # yellow
        elif self.color == 3:
            shape_color = (0,255,255)  # cyan
        elif self.color == 4:
            shape_color = (255,165,0)  # orange

        text_bg = (0,0,0)  # background of the text display (black)
        font_size = int((self.width + self.height)*scale*.2)
        if font_size > 20:
            font_size = 20
        font = pygame.font.SysFont("Times New Roman", size=font_size)  # font to use for the name label

        # Determines which shape to draw (0 = circle, 1 = rectangle)
        if self.shape == 0:
            pygame.draw.ellipse(surface=screen, color=shape_color,
                                rect=(image_x + self.x*scale - (self.width*scale/2), image_y + self.y*scale - (self.height*scale/2),
                                      self.width*scale, self.height*scale),
                                width=self.line_width)
        elif self.shape == 1:
            pygame.draw.rect(surface=screen, color=shape_color,
                             rect=(image_x + self.x*scale - (self.width*scale/2), image_y + self.y*scale - (self.height*scale/2),
                                   self.width*scale, self.height*scale),
                             width=self.line_width)

        # Displays the name of the inspection item
        if self.display_name:
            name_label = font.render(self.name, True, shape_color, text_bg)
            screen.blit(name_label, (image_x + self.x*scale, image_y + self.y*scale -
                                     (self.height*scale/2) - (self.line_width*4.5)))


# Method: gui
# Purpose: Creates a pygame GUI
# Parameters:
#   String image_file: filename of the image to display
#   Array shapes_to_draw: Array of ShapeToDraw objects to display
# Returns: N/A
def gui(image_1_file, image_2_file, image_3_file, inspection_results, json_file):

    # Initialize the GUI
    pygame.init()
    size = (1920,1020)  # Size of the window
    screen = pygame.display.set_mode(size)  # Create a surface with the window size created above
    pygame.display.set_caption("Indicon Inspection Results")  # Sets the title of the window

    # More Initialization
    text_color = (220,220,225)  # Light gray
    background = (51,51,51)  # Dark Gray
    font = pygame.font.SysFont("Times New Roman", size=22)  # Font to use for text on the GUI

    screen.fill(background)
    image_1_image = pygame.image.load(image_1_file).convert()
    image_2_image = pygame.image.load(image_2_file).convert()
    image_3_image = pygame.image.load(image_3_file).convert()

    # Button object allows the images to be manipulated easily
    image_1_scale = 0.8
    image_1 = Button.Button(x=510, y=35, image=image_1_image, scale=image_1_scale)
    image_1.draw(screen)

    image_2_scale = 0.8
    image_2 = Button.Button(x=510, y=355, image=image_2_image, scale=image_2_scale)
    image_2.draw(screen)

    image_3_scale = 0.8
    image_3 = Button.Button(x=510, y=675, image=image_3_image, scale=image_3_scale)
    image_3.draw(screen)

    shapes_to_draw, failed_inspections = inspection_results

    image_offset_x = 0
    image_offset_y = 0
    image_scale = 1

    # Display all ShapeToDraw objects
    for shape in shapes_to_draw:
        if shape.image == '1':
            image_offset_x, image_offset_y = image_1.rect.topleft
            image_scale = image_1_scale
        elif shape.image == '2':
            image_offset_x, image_offset_y = image_2.rect.topleft
            image_scale = image_2_scale
        elif shape.image == '3':
            image_offset_x, image_offset_y = image_3.rect.topleft
            image_scale = image_3_scale
        shape.draw_shape(screen, image_offset_x, image_offset_y, image_scale)

    # Set clock cycle to make the program less intensive
    clock = pygame.time.Clock()

    # Boolean value to show whether or not the current gui() instance is running
    running = True
    count = 0
    index = 0
    table_x = image_2.rect.right + 100
    table_y = image_2.rect.bottom
    table_rect = pygame.Rect(table_x, table_y, 400, 32)
    live_image_scale = 0.1

    # Runtime loop controls the GUI
    while running:

        clock.tick(60)  # Makes the program less intensive

        # Handles user events
        for event in pygame.event.get():

            # Exits the program if the user closes the window
            if event.type == pygame.QUIT:
                running = False

        if len(failed_inspections) > 0:
            if count % 190 == 0:
                clear_fail_rect = pygame.Rect(table_rect.left - 20, 0, screen.get_rect().right - image_2.rect.right,
                                              screen.get_height())
                pygame.draw.rect(screen, background, clear_fail_rect)
                table_label = font.render(failed_inspections[index].inspection_name
                                          + " result parameters:", True, (255, 0, 0))
                screen.blit(table_label, (table_rect.left, table_y - 28))
                failed_inspections[index].fill_table(screen, table_rect)
                failed_inspections[index].display_image(screen, table_x, image_1.rect.top, live_image_scale)
                failed_inspections[index].draw_shape(screen, table_x, image_1.rect.top, live_image_scale)
                index = (index + 1) % len(failed_inspections)

        # TODO: Make sure this gets the data from the TCP message properly
        system_name = str(data)
        # system_name = 'RHF122133072454630_YenFeng'
        # Get the most recent json file from the directory
        json_files = glob.iglob(directory + '\\' + '*.json')
        system_json_files = []
        count = 0
        for file in json_files:
            if file.__contains__(system_name):
                system_json_files.insert(count, file)
                count = count + 1
        latest_json = max(system_json_files, key=os.path.getctime)

        # if there is a new file, update the information and display
        if latest_json != json_file:
            running = False
            print(latest_json)
            gui(image_1_file, image_2_file, image_3_file, get_inspection(latest_json), latest_json)

        count = count + 1

        pygame.display.flip()


# Method: main
# Purpose: Starts the initial run-through of the program
# Parameters: N/A
# Returns: N/A
def main():

    # Do nothing until the TCP message is initially sent
    while data is None:
        looping = True

    # TODO: Make sure this gets the data from the TCP message properly
    system_name = str(data)
    # system_name = 'RHF122133072454630_YenFeng'
    # Get the most recent json file from the directory
    json_files = glob.iglob(directory + '\\' + '*.json')
    system_json_files = []
    count = 0
    for file in json_files:
        if file.__contains__(system_name):
            system_json_files.insert(count, file)
            count = count + 1
            print(file + '\n')
    latest_json = max(system_json_files, key=os.path.getctime)
    file_name = latest_json  # File name of the initial json file

    # TODO: Change these image files to the static image files to be used (Delete 2 and 3 to use a collage)
    image_1_file = "IP_Image_1.png"  # Image file to display on the GUI
    image_2_file = "IP_Image_1.png"
    image_3_file = "IP_Image_1.png"

    gui(image_1_file, image_2_file, image_3_file, get_inspection(file_name), file_name)


if __name__ == "__main__":
    main()

