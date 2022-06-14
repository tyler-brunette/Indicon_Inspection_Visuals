import json
import os.path
import pygame
from pygame import K_v, K_LCTRL
import Button

current_directory = os.getcwd()  # Current directory of the python script
global directory
directory = 'D:\\Images\\Left\\2022-05-16\\RHF122133072454630'  # TODO: Directory containing the live images


# Method: save_shape_data
# Purpose: Adds a ShapeToDraw object to the Shape array in the json file
# Parameters:
#   ShapeToDraw shape: ShapeToDraw object to add to the json file
# Returns: N/A
def save_shape_data(shape, output_file):

    file = output_file
    shape_to_save = shape.__dict__

    shape_json = open(file)
    shape_data = json.load(shape_json)
    shape_data['Shapes'].append(shape_to_save)

    with open(file, "w") as outfile:
        json.dump(obj=shape_data, indent=4, fp=outfile)


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
#   String key: key that corresponds to the ResultParameters
#   String image: image to draw the shape on
# Returns: N/A
class ShapeToDraw:

    # Method: __init__
    # Purpose: Initializes a ShapeToDraw object
    # Parameters: See Above
    # Returns: N/A
    def __init__(self, name, shape, color, display_name, x, y, height, width, key, image):
        self.name = name
        self.shape = shape
        self.color = color
        self.display_name = display_name
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.key = key
        self.image = image
        self.line_width = 5

    # Method: draw_shape
    # Purpose: draws a shape on the screen
    # Parameters:
    #   Surface screen: surface to draw the shape on
    #   Int image_x: x position of the image to draw the shape on (left)
    #   Int image_y: y position of the image to draw the shape on (top)
    #   Float scale: scale factor of the image
    # Returns:
    #   Rect rect: rectangle of the shape
    def draw_shape(self, screen, image_x, image_y):

        shape_color = (255, 0, 0)
        match self.color:
            case 0:
                shape_color = (0,255,0)
            case 1:
                shape_color = (255,0,0)
            case 2:
                shape_color = (255, 240, 31)
            case 3:
                shape_color = (0,255,255)
            case 4:
                shape_color = (255,165,0)

        text_bg = (0,0,0)
        font = pygame.font.SysFont("Times New Roman", size=12)
        if self.shape == 0:
            pygame.draw.ellipse(surface=screen, color=shape_color,
                                rect=(image_x + self.x - (self.width / 2), image_y + self.y - (self.height / 2),
                                      self.width, self.height),
                                width=self.line_width)
        elif self.shape == 1:
            pygame.draw.rect(surface=screen, color=shape_color,
                             rect=(image_x + self.x - (self.width/2), image_y + self.y - (self.height/2),
                                   self.width, self.height),
                             width=self.line_width)

        rect = pygame.Rect(image_x + self.x - (self.width / 2), image_y + self.y - (self.height / 2),
                           self.width, self.height)

        if self.display_name:
            name_label = font.render(self.name, True, shape_color, text_bg)
            screen.blit(name_label, (image_x + self.x, image_y + self.y - (self.height/2) - (self.line_width*3)))

        return rect

    # Method: get_scaled_shape
    # Purpose: gets the scaled version of the shape that can be displayed on the image with a variable scale
    # Parameters:
    #   Float scale: scale factor of the image
    # Returns:
    #   ShapeToDraw scaled_shape: scaled version of the shape
    def get_scaled_shape(self, scale):
        name = self.name
        shape = self.shape
        color = self.color
        display_name = self.display_name
        x = self.x * 1/scale
        y = self.y * 1/scale
        height = self.height * 1/scale
        width = self.width * 1/scale
        key = self.key
        image = self.image
        scaled_shape = ShapeToDraw(name, shape, color, display_name, x, y, height, width, key, image)
        return scaled_shape


# Method: set_user_text
    # Purpose: modifies a string
    # Parameters:
    #   obj event: holds data about the event that occurred
    #   String user_text: string to edit
    # Returns:
    #   String user_text: edited version of the string
def set_user_text(event, user_text):
    # Check for backspace
    keys = pygame.key.get_pressed()
    if event.key == pygame.K_BACKSPACE:

        # get text input from 0 to -1 i.e. end.
        user_text = user_text[:-1]
    # if CTRL + V then append the clipboard text to user_text
    elif keys[K_v] and keys[K_LCTRL]:
        clipboard = pygame.scrap.get(pygame.SCRAP_TEXT)
        clipboard = str(clipboard)
        user_text = user_text + clipboard[2:len(clipboard) - 5]

    # Unicode standard is used for string formation
    else:
        user_text += event.unicode
    return user_text


# Method: gui
# Purpose: Creates and runs a pygame GUI
# Parameters:
#   Int pos_x: x position of the shape (left)
#   Int pos_y: y position of the shape (top)
#   String height: height of the shape
#   String width: width of the shape
#   String shape: type of shape to draw (0 = ellipse, 1 = rectangle)
#   String name: name of the shape (shown on label above shape)
#   String image_number: which image the shape is linked to
#   Bool move_shape: Shows whether the shape is currently being moved or not
#   String key: key that corresponds to the ResultParameters
#   String image_scale: scale factor of the image
#   String live_image: live image filename
# Returns: N/A
def gui(pos_x, pos_y, height, width, shape, name, image_number, move_shape, key, image_scale, live_image):

    # Initialize the GUI
    pygame.init()
    size = (1920,1010)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Indicon Inspection Results")

    # Color constants
    text_color = (220,220,225)
    background = (51,51,51)
    dark_text_color = (20,20,20)

    # Initialize images for buttons
    new_shape_button_image = pygame.image.load("generate_button.png").convert()
    save_static_data_button_image = pygame.image.load("save_static_data_button.png").convert()
    save_live_data_button_image = pygame.image.load("save_live_data_button.png").convert()

    screen.fill(background)
    font = pygame.font.SysFont("Times New Roman", size=22)

    # Constants for input box dimensions
    input_box_width = 125
    input_box_height = 30

    # Initialize input boxes
    image_scale_input_label = font.render("scale:", True, text_color)
    screen.blit(image_scale_input_label, (25, 50))
    image_scale_input_rect = pygame.Rect(100, 50, input_box_width, input_box_height)
    image_scale_text = image_scale

    shape_key_input_label = font.render("key:", True, text_color)
    screen.blit(shape_key_input_label, (25, 100))
    shape_key_input_rect = pygame.Rect(100, 100, input_box_width, input_box_height)
    shape_key_text = key

    image_input_label = font.render("image:", True, text_color)
    screen.blit(image_input_label, (25, 150))
    image_input_rect = pygame.Rect(100, 150, input_box_width, input_box_height)
    image_text = image_number

    pos_x = pos_x
    pos_y = pos_y

    height_input_label = font.render("height:", True, text_color)
    screen.blit(height_input_label, (25, 200))
    height_input_rect = pygame.Rect(100, 200, input_box_width, input_box_height)
    height_text = height

    width_input_label = font.render("width:", True, text_color)
    screen.blit(width_input_label, (25, 250))
    width_input_rect = pygame.Rect(100, 250, input_box_width, input_box_height)
    width_text = width

    shape_input_label = font.render("shape:", True, text_color)
    screen.blit(shape_input_label, (25, 300))
    shape_input_rect = pygame.Rect(100, 300, input_box_width, input_box_height)
    shape_text = shape

    name_input_label = font.render("name:", True, text_color)
    screen.blit(name_input_label, (25, 350))
    name_input_rect = pygame.Rect(100, 350, input_box_width, input_box_height)
    name_text = name

    live_image_input_label = font.render("live image:", True, text_color)
    screen.blit(live_image_input_label, (25, 400))
    live_image_input_rect = pygame.Rect(140, 400, input_box_width, input_box_height)
    live_image_text = live_image

    # Initialize buttons
    new_shape_button = Button.Button(x=75, y=450, image=new_shape_button_image, scale=1)
    new_shape_button.draw(screen)

    save_static_data_button = Button.Button(x=75, y=500, image=save_static_data_button_image, scale=1)
    save_static_data_button.draw(screen)

    save_live_data_button = Button.Button(x=75, y=550, image=save_live_data_button_image, scale=1)
    save_live_data_button.draw(screen)

    # Chooses the displayed image based on the user's input
    image_file = "doge_wink.JPG"  # Default Image
    # TODO: Put your images here that you want to draw shapes on
    match image_text:
        case '1':
            image_file = "IP_Image_1.png"  # Ex: Top View
        case '2':
            image_file = "IP_Image_1.png"  # Ex: Front View
        case '3':
            image_file = "IP_Image_1.png"  # Ex: Bottom View
        case '4':
            if live_image_text == "":
                image_file = image_file
            else:
                image_file = directory + '\\' + live_image_text

    image = pygame.image.load(image_file).convert()

    # Display the image on the screen
    image_label = font.render("Image " + image_text + ":", True, text_color)
    screen.blit(image_label, (420, 35))
    image_scale = float(image_scale_text)
    image_display = Button.Button(x=510, y=35, image=image, scale=image_scale)
    image_display.draw(screen)

    image_offset_x, image_offset_y = image_display.rect.topleft

    # Initialize the shape to be drawn on the screen
    shape_to_draw = ShapeToDraw(name=name_text, shape=int(shape_text), color=1, display_name=1, x=pos_x, y=pos_y,
                                height=float(height_text), width=float(width_text), key=shape_key_text,
                                image=image_text)
    # draw shape and get the rect of the shape
    shape_rect = shape_to_draw.draw_shape(screen, image_offset_x, image_offset_y)

    # Set clock cycle to make the program less intensive
    clock = pygame.time.Clock()

    running = True  # Boolean value to show whether the current gui() instance is running or not

    # Booleans show whether the given input box is active or not
    height_active = False
    width_active = False
    shape_active = False
    name_active = False
    image_active = False
    shape_key_active = False
    scale_active = False
    live_image_active = False

    # Shows whether the shape is being moved or not
    move_shape = move_shape

    # Initialize the clipboard capability
    pygame.scrap.init()
    pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

    # Runtime loop controls the GUI
    while running:

        clock.tick(60)

        # Handles user events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Reset all input box bools to False
                height_active = False
                width_active = False
                shape_active = False
                name_active = False
                image_active = False
                shape_key_active = False
                scale_active = False
                live_image_active = False

                # Set move_shape to True if the user clicks the shape
                if shape_rect.collidepoint(event.pos):
                    move_shape = True

                # If new shape button is clicked, refresh the display with the new shape data
                if new_shape_button.is_clicked():
                    running = False
                    gui(pos_x, pos_y, height_text, width_text, shape_text, name_text,
                        image_text, False, shape_key_text, image_scale_text, live_image_text)

                # If one of the save data buttons is clicked, save the shape data to the correct json file
                if save_static_data_button.is_clicked():
                    output_file = "ShapeData.json"  # TODO: Change to your static image shape data json file
                    save_shape_data(shape_to_draw.get_scaled_shape(image_scale), output_file)

                if save_live_data_button.is_clicked():
                    output_file = "LiveImageShapes.json"  # TODO: Change to your live image shape data json file
                    save_shape_data(shape_to_draw.get_scaled_shape(image_scale), output_file)

                # If the user clicks an input box, set its boolean as active
                if height_input_rect.collidepoint(event.pos):
                    height_active = True
                elif width_input_rect.collidepoint(event.pos):
                    width_active = True
                elif shape_input_rect.collidepoint(event.pos):
                    shape_active = True
                elif name_input_rect.collidepoint(event.pos):
                    name_active = True
                elif image_input_rect.collidepoint(event.pos):
                    image_active = True
                elif shape_key_input_rect.collidepoint(event.pos):
                    shape_key_active = True
                elif image_scale_input_rect.collidepoint(event.pos):
                    scale_active = True
                elif live_image_input_rect.collidepoint(event.pos):
                    live_image_active = True

            # Set move_shape to False if the user releases the mouse
            if event.type == pygame.MOUSEBUTTONUP:
                move_shape = False

            if event.type == pygame.KEYDOWN:

                # If an input box is active, add the text to that box
                if height_active:
                    height_text = set_user_text(event, height_text)
                elif width_active:
                    width_text = set_user_text(event, width_text)
                elif shape_active:
                    shape_text = set_user_text(event, shape_text)
                elif name_active:
                    name_text = set_user_text(event, name_text)
                elif image_active:
                    image_text = set_user_text(event, image_text)
                elif shape_key_active:
                    shape_key_text = set_user_text(event, shape_key_text)
                elif scale_active:
                    image_scale_text = set_user_text(event, image_scale_text)
                elif live_image_active:
                    live_image_text = set_user_text(event, live_image_text)

        # Update the position of the shape if it is being moved
        if move_shape:
            running = False
            pos_x, pos_y = pygame.mouse.get_pos()
            gui(pos_x - image_offset_x, pos_y - image_offset_y, height_text, width_text, shape_text, name_text,
                image_text, True, shape_key_text, image_scale_text, live_image_text)

        # Draw all input boxes
        pygame.draw.rect(screen, text_color, rect=height_input_rect)
        pygame.draw.rect(screen, text_color, rect=width_input_rect)
        pygame.draw.rect(screen, text_color, rect=shape_input_rect)
        pygame.draw.rect(screen, text_color, rect=name_input_rect)
        pygame.draw.rect(screen, text_color, rect=image_input_rect)
        pygame.draw.rect(screen, text_color, rect=shape_key_input_rect)
        pygame.draw.rect(screen, text_color, rect=image_scale_input_rect)
        pygame.draw.rect(screen, text_color, rect=live_image_input_rect)

        # Create labels with the text
        height_label = font.render(height_text, True, dark_text_color)
        width_label = font.render(width_text, True, dark_text_color)
        shape_label = font.render(shape_text, True, dark_text_color)
        name_label = font.render(name_text, True, dark_text_color)
        image_label = font.render(image_text, True, dark_text_color)
        shape_key_label = font.render(shape_key_text, True, dark_text_color)
        image_scale_label = font.render(image_scale_text, True, dark_text_color)
        live_image_label = font.render(live_image_text, True, dark_text_color)

        # Draw all labels
        screen.blit(height_label, height_input_rect.topleft)
        screen.blit(width_label, width_input_rect.topleft)
        screen.blit(shape_label, shape_input_rect.topleft)
        screen.blit(name_label, name_input_rect.topleft)
        screen.blit(image_label, image_input_rect.topleft)
        screen.blit(shape_key_label, shape_key_input_rect.topleft)
        screen.blit(image_scale_label, image_scale_input_rect.topleft)
        screen.blit(live_image_label, live_image_input_rect.topleft)

        # Extend the input boxes if needed
        height_input_rect.w = max(100, height_label.get_width() + 10)
        width_input_rect.w = max(100, width_label.get_width() + 10)
        shape_input_rect.w = max(100, shape_label.get_width() + 10)
        name_input_rect.w = max(100, name_label.get_width() + 10)
        image_input_rect.w = max(100, image_label.get_width() + 10)
        shape_key_input_rect.w = max(100, shape_key_label.get_width() + 10)
        image_scale_input_rect.w = max(100, image_scale_label.get_width() + 10)
        live_image_input_rect.w = max(100, live_image_label.get_width() + 10)

        pygame.display.flip()


# Method: main
# Purpose: Starts the initial run-through of the program
# Parameters: N/A
# Returns: N/A
def main():
    # Initial gui() call
    gui(pos_x=0, pos_y=0, height="100", width="100", shape="0", name="shape_test", image_number="1", move_shape=False,
        key="", image_scale="1", live_image="")


if __name__ == "__main__":
    main()

