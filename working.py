import os
import copy
import yaml
import time

#process
#  locations set in working_parts.ods 
#  export to working_parts.csv
#  put components on the right side of the board
#  run this script

#import a library to plot points onto an image
import cv2
import numpy as np

#scales
configuration_scale_name = "tool_scale_76_mm_width_114_mm_height_20_mm_depth_1000_gram_capacity_aliexpress_jewelry_scale"

def main(**kwargs):
    create_scale_configuration()

    configuration_file = "configuration/oomlout_tdpbmct_tool_scale.yaml"
    with open(configuration_file, 'r') as file:
        print(f"reading from {configuration_file}")
        scale_configurations = yaml.load(file, Loader=yaml.FullLoader)

    scale_configuration = scale_configurations[0]
    print(f"scale_configuration: {scale_configuration["name"]}")

    create_configuration_overlay_image(scale_configuration)

    
    run_test(scale_configuration)

    #while False:
    while True:
        #from camera
        value = get_reading_from_camera(scale_configuration)
        print(f"value: {value}")
        #time.sleep(1)


def run_test(scale_configuration):
    #from image
    image_names = []
    image_names.append(f"test_images/test_image_scale_196_1_g.jpg")
    image_names.append(f"test_images/test_image_scale_225_0_g.jpg")
    image_names.append(f"test_images/test_image_scale_227_4_g.jpg")

    for image_name in image_names:
        print(f"image_name: {image_name}")
        value = get_reading_from_file(scale_configuration, image_name=image_name)
        print(f"value: {value} g")


    
def create_configuration_overlay_image(scale_configuration, image=None, save_image=True):
    
    

    #import a library to plot points onto an image

    import cv2
    import numpy as np

    #read the image
    #test if image is an cv2 image
    if image is not None:    
        img = image
    else:
        image_test = "test_images/test.jpg"
        img = cv2.imread(image_test)

    #if image isn't colour make a colour version with it as the base
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


    #plot the segment test coordinates one by one on the image
    colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255),(255,255,255)]

    number_of_digits = scale_configuration["number_of_digits"]
    digit_start_coordinates = scale_configuration["digit_start_coordinates"]
    segment_test_coordinates = scale_configuration["segment_test_coordinates"]
    for i in range(number_of_digits):
    #for i in range(1):
        x = digit_start_coordinates[i][0]
        y = digit_start_coordinates[i][1]
        color = colors[i]
        #add circle of color color
        cv2.circle(img, (x,y), 10, color, -1)
        #add image offsets
        for j in range(len(segment_test_coordinates)):
            xx = x + segment_test_coordinates[j][0]
            yy = y + segment_test_coordinates[j][1]
            cv2.circle(img, (xx,yy), 5, color, -1)

    #save the image
    image_overlay = "test_images/test_create_configuration_overlay_image.jpg"
    print(f"saving to {image_overlay}")
    cv2.imwrite(image_overlay, img)

    return img




def create_scale_configuration():
    file_configuration  = "configuration/oomlout_tdpbmct_tool_scale.yaml"

    scale_configurations = []

    scale_name = "tool_scale_76_mm_width_114_mm_height_20_mm_depth_1000_gram_capacity_aliexpress_jewelry_scale"
    scale_configuration = {}
    scale_configuration["name"] = scale_name  
    scale_configuration["display_style"] = "seven_segment"
    scale_configuration["number_of_digits"] = 5
    #configuration of digits
    scale_configuration["digit_start_coordinates"] = []
    x = 606
    y = 130
    scale_configuration["digit_start_coordinates"].append([x,y])
    shift_x = -100
    shift_y = 0
    for i in range(6):
        x += shift_x
        y += shift_y
        scale_configuration["digit_start_coordinates"].append([x,y])
        


    #configuration of segments
    #clockwise from top middle is last
    scale_configuration["segment_test_coordinates"] = []
    x_left_top = 18
    x_left_bottom = 10
    x_middle = 40
    x_right_top = 72
    x_right_bottom = 64
    
    y_top = 12
    y_top_middle = 44
    y_middle = 81
    y_bottom_middle = 115
    y_bottom = 145
    
    scale_configuration["segment_test_coordinates"].append([x_middle,y_top])
    scale_configuration["segment_test_coordinates"].append([x_right_top,y_top_middle])
    scale_configuration["segment_test_coordinates"].append([x_right_bottom,y_bottom_middle])
    scale_configuration["segment_test_coordinates"].append([x_middle,y_bottom])
    scale_configuration["segment_test_coordinates"].append([x_left_bottom,y_bottom_middle])
    scale_configuration["segment_test_coordinates"].append([x_left_top,y_top_middle])
    scale_configuration["segment_test_coordinates"].append([x_middle,y_middle])

    scale_configurations.append(scale_configuration)

    #save configuration
    with open(file_configuration, 'w') as file:
        print(f"writing to {file_configuration}")
        documents = yaml.dump(scale_configurations, file)


def get_reading_from_file(scale_configuration, image_name="test_images/test.jpg"):    
    #read the image
    img = cv2.imread(image_name)

    return get_reading_from_image(img, scale_configuration)

def get_reading_from_camera(scale_configuration):
    #create a video capture object
    cap = cv2.VideoCapture(1)
    #set 720 resolution
    cap.set(3, 1280)
    #get an image from the device    
    ret, frame = cap.read()
    #release the video capture object
    cap.release()

    image = frame

    

    #save image as test_images/test_raw.jpg
    #image_name = "test_images/test_raw.jpg"
    #print(f"saving to {image_name}")
    #cv2.imwrite(image_name, image)
    

    return get_reading_from_image(image, scale_configuration)

#def get_reading_from_image(image, scale_configuration, save_image=True):
def get_reading_from_image(image, scale_configuration, save_image=False):    
    image = process_image(image, scale_configuration)   


    segments = []
    for i in range(scale_configuration["number_of_digits"]):
        segment = []
        digit_start_coordinates = scale_configuration["digit_start_coordinates"][i]
        for j in range(7):
            segment_x = digit_start_coordinates[0] + scale_configuration["segment_test_coordinates"][j][0]
            segment_y = digit_start_coordinates[1] + scale_configuration["segment_test_coordinates"][j][1]
            #get the brigtness for a 3x3 pixel area
            brightness_total = 0
            for x in range(-1,2):
                for y in range(-1,2):
                    pixel_value = image[segment_y+y, segment_x+x]
                    #reds int value
                    value = int(pixel_value)
                    brightness_pixel = value
                    brightness_total += brightness_pixel/9
            threshold = 127
            if brightness_total > threshold:
                segment.append(1)
            else:
                segment.append(0)        
        segment_original = copy.deepcopy(segment)
        segment = None
        #segment.append(brightness_total)
        segment_test = []
        segment_test.append([0,0,0,0,0,0,1]) #0
        segment_test.append([1,0,0,1,1,1,1]) #1
        segment_test.append([0,0,1,0,0,1,0]) #2
        segment_test.append([0,0,0,0,1,1,0]) #3
        segment_test.append([1,0,0,1,1,0,0]) #4
        segment_test.append([0,1,0,0,1,0,0]) #5
        segment_test.append([0,1,0,0,0,0,0]) #6
        segment_test.append([0,0,0,1,1,1,1]) #7
        segment_test.append([0,0,0,0,0,0,0]) #8
        segment_test.append([0,0,0,0,1,0,0]) #9
        segment_test.append([1,1,1,1,1,1,1]) # blank
        
        
        
        for i in range(0,len(segment_test)):
            match = True
            for j in range(0,len(segment_test[i])):
                if segment_test[i][j] != segment_original[j]:
                    match = False
                    break            
            if match:
                segment = i
            
            
            
        segments.append(segment)
    try:
        reading = 0
        for i in range(len(segments)-1,-1,-1):
            if segments[i] == 10:
                segments[i] = 0
            reading = reading * 10 + segments[i]
            
        reading = reading/10
    except:
        reading = "error"
    if reading == 8888.8:
        reading = "error turned off"


    if save_image:
        #add calibration dots
        image = create_configuration_overlay_image(scale_configuration, image, save_image=False)
        #add reading to middle right 
        text_size = 5
        text_thickness = 10
        #choose a bold font
        font = cv2.FONT_HERSHEY_SIMPLEX

        text = f"{reading} g"
        text_location = (200, 500)
        text_color = (0, 0, 255)
        cv2.putText(image, text, text_location, font, text_size, text_color, text_thickness, cv2.LINE_AA)

        #save image as test_images/test_raw.jpg
        image_name = "test_images/test_get_reading_from_image.jpg"
        print(f"saving to {image_name}")
        cv2.imwrite(image_name, image)


    return reading

#def process_image(image, scale_configuration, save_image=True, save_configuration=True):
def process_image(image, scale_configuration, save_image=False, save_configuration=False):
    pass

    #increase contrast
    alpha = 1.5
    beta = 0
    image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    #convert to black and white with adjustable threshold
    threshold = 225
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)






    if save_image:
        #save image as test_images/test_raw.jpg
        image_name = "test_images/test_process_image.jpg"
        print(f"saving to {image_name}")
        cv2.imwrite(image_name, image)

    if save_configuration:
        create_configuration_overlay_image(scale_configuration, image)

    return image

if __name__ == '__main__':
    kwargs = {}

    main(**kwargs)