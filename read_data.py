'''

read_data.py

The code is designed to extract and analyze screen states from images related to a game using Optical Character 
Recognition (OCR) and image processing techniques. It begins by reading an image file and extracting text using 
the pytesseract library. Based on the extracted text, it checks if the screen matches one of several predefined 
states, such as "Waiting to Start," "Race Results," "Live Game," "Game Type Select," "Race Select," or 
"Race Select Play." 

If no state is detected, the code applies preprocessing techniques, such as grayscale conversion and advanced 
image processing (inverting, thresholding, blurring, and edge detection), to improve text extraction and screen
state detection.

If the preprocessing steps do not yield a valid result, the code compares the current image against reference 
images using template matching to find the highest correlation. Based on the highest correlation score, the 
screen state is predicted. The code then returns the determined screen states, allowing further interaction 
or decisions in the game flow based on the detected state.

'''

import cv2
import pytesseract
import numpy as np
import os

# Function to check the screen state based on extracted text
def check_screen_state_from_text(extracted_text):
    waiting_to_start = False
    race_results_screen = False
    live_game = False
    game_type_select = False
    race_select = False
    race_select_play = False
    
    # Check if the string 'Waiting To Start' is in the extracted text
    if 'Waiting To Start' in extracted_text:
        waiting_to_start = True
        print("Screen is in 'Waiting To Start' state.")

    # Check if the extracted text contains 'Race Results' or 'Race' and 'Results'
    if 'Race' in extracted_text and 'Results' in extracted_text:
        race_results_screen = True
        print("Screen is in 'Race Results' state.")

    # Check if the string 'Alienated' is in the extracted text and 'Play Again' is not
    if 'Alienated' in extracted_text and 'Play Again' not in extracted_text:
        live_game = True
        print("Screen is in 'Live Game' state.")
    
    # Check if the string 'Build:' is in the extracted text
    if 'Build:' in extracted_text:
        game_type_select = True
        print("Screen is in 'Game Type Select' state.")
        
    # Check if the string contains 'Race' AND 'Standard' AND NOT 'Play' in the extracted text
    if 'Race' in extracted_text and 'Standard' in extracted_text and 'Play' not in extracted_text:
        race_select = True
        print("Screen is in 'Race Select' state.")
        
    # Check if the string contains 'Race' AND 'Standard' AND 'Play' in the extracted text
    if 'Race' in extracted_text and 'Standard' in extracted_text and 'Play' in extracted_text:
        race_select_play = True
        print("Screen is in 'Race Select Play' state.")
    
    return waiting_to_start, race_results_screen, live_game, game_type_select, race_select, race_select_play

# Function for Level 2 Grayscale Preprocessing
def grayscale_preprocessing(img):
    # Convert image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding for better results on complex backgrounds
    processed_img = cv2.adaptiveThreshold(
        gray_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    return processed_img

# Function for Level 3 Advanced Preprocessing
def advanced_preprocessing(img):
    # Convert image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image (turn white areas into black and black into white)
    inverted_img = cv2.bitwise_not(gray_img)

    # Apply adaptive thresholding for better results on complex backgrounds
    processed_img = cv2.adaptiveThreshold(
        inverted_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Apply Gaussian Blur to reduce noise
    blurred_img = cv2.GaussianBlur(processed_img, (5, 5), 0)
    
    # Optional: Use edge detection to emphasize the features of the text
    edges_img = cv2.Canny(blurred_img, threshold1=100, threshold2=200)

    return edges_img

# Function to compare the current image with reference images and find the highest correlation
def compare_with_reference_images(current_img, reference_images_dir):
    correlation_scores = {}
    
    # Convert the current image to grayscale and ensure it's 8-bit
    current_img_gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
    current_img_gray = np.uint8(current_img_gray)  # Ensure it's in 8-bit format
    
    # Get all reference images in the directory
    reference_images = [os.path.join(reference_images_dir, f) for f in os.listdir(reference_images_dir) if f.endswith('.png')]
    
    # Iterate over each reference image
    for ref_img_path in reference_images:
        ref_img = cv2.imread(ref_img_path, cv2.IMREAD_GRAYSCALE)
        
        if ref_img is None:
            print(f"Failed to load reference image: {ref_img_path}")
            continue
        
        # Ensure the reference image is also in 8-bit format
        ref_img = np.uint8(ref_img)  # Ensure it's in 8-bit format
        
        # Match template using cv2.matchTemplate
        result = cv2.matchTemplate(current_img_gray, ref_img, cv2.TM_CCOEFF_NORMED)
        
        # Get the highest correlation value
        correlation = cv2.minMaxLoc(result)[1]
        
        # Store the correlation value
        correlation_scores[ref_img_path] = correlation
    
    # Rank the correlation scores in descending order
    sorted_correlation_scores = sorted(correlation_scores.items(), key=lambda x: x[1], reverse=True)

    # Debugging: print correlation values
    print("Correlation Scores (Ranked):")
    for ref_img_path, score in sorted_correlation_scores:
        print(f"Reference Image: {ref_img_path}, Correlation: {score}")
    
    return sorted_correlation_scores

# Main function to check the screen state from the image
def check_screen_state(image_path, reference_images_dir):
    # Read the current image using OpenCV
    current_img = cv2.imread(image_path)

    # Step 1: Use pytesseract to extract the text directly from the image
    extracted_text = pytesseract.image_to_string(current_img)
    print("Extracted Text (No Preprocessing):")
    print(extracted_text)
    
    # Check screen state based on the extracted text
    waiting_to_start, race_results_screen, live_game, game_type_select, race_select, race_select_play = check_screen_state_from_text(extracted_text)

    # If no valid states were detected, apply grayscale preprocessing
    if not (waiting_to_start or race_results_screen or live_game or game_type_select or race_select or race_select_play):
        print("No valid screen state detected. Applying grayscale preprocessing...")
        
        # Step 2: Apply grayscale preprocessing
        processed_img = grayscale_preprocessing(current_img)

        # Use pytesseract again on the processed image
        extracted_text = pytesseract.image_to_string(processed_img)
        print("Reprocessed Extracted Text (Grayscale Preprocessing):")
        print(extracted_text)

        # Recheck the screen state after preprocessing
        waiting_to_start, race_results_screen, live_game, game_type_select, race_select, race_select_play = check_screen_state_from_text(extracted_text)

    # If still no valid states detected, apply advanced preprocessing
    if not (waiting_to_start or race_results_screen or live_game or game_type_select or race_select or race_select_play):
        print("No valid screen state detected. Applying advanced preprocessing...")
        
        # Step 3: Apply advanced preprocessing
        processed_img = advanced_preprocessing(current_img)

        # Use pytesseract again on the processed image
        extracted_text = pytesseract.image_to_string(processed_img)
        print("Reprocessed Extracted Text (Advanced Preprocessing):")
        print(extracted_text)

        # Recheck the screen state after advanced preprocessing
        waiting_to_start, race_results_screen, live_game, game_type_select, race_select, race_select_play = check_screen_state_from_text(extracted_text)

    # If still no valid states detected, compare with reference images
    if not (waiting_to_start or race_results_screen or live_game or game_type_select or race_select or race_select_play):
        print("No valid screen state detected. Comparing with reference images...")
        
        # Compare with reference images and get correlation scores
        sorted_correlation_scores = compare_with_reference_images(current_img, reference_images_dir)
        
        # Print correlation values and ranks
        print("Correlation scores with reference images (ranked):")
        for ref_img_path, score in sorted_correlation_scores:
            print(f"{ref_img_path}: {score}")

        # Predict the screen state based on highest correlation
        highest_score_ref_img = sorted_correlation_scores[0][0]
        
        # Check which reference image corresponds to which state
        if "Game_Type" in highest_score_ref_img:
            game_type_select = True
            print("Predicted Screen State: Game Type Select")
        elif "Live_Race_Info" in highest_score_ref_img:
            live_game = True
            print("Predicted Screen State: Live Game")
        elif "Race_Results" in highest_score_ref_img:
            race_results_screen = True
            print("Predicted Screen State: Race Results")
        elif "Waiting_to_Start" in highest_score_ref_img:
            waiting_to_start = True
            print("\nPredicted Screen State: Waiting to Start")
        elif "Race_Select" in highest_score_ref_img:
            race_select = True
            print("\nPredicted Screen State: Race Select")
        elif "Race_Select_Play" in highest_score_ref_img:
            race_select_play = True
            print("\nPredicted Screen State: Race Select Play")
        
    # Return the final states
    return waiting_to_start, race_results_screen, live_game, game_type_select, race_select, race_select_play

# Path to your image and reference images folder
image_path = r'C:\Users\joshp\Desktop\Marbles\Images\Target\0001.png'  # Update the path accordingly
reference_images_dir = r'C:\Users\joshp\Desktop\Marbles\Images'  # Folder containing reference images

# Call the function and get the result
waiting_to_start, race_results_screen, live_game, game_type_select, race_select, race_select_play = check_screen_state(image_path, reference_images_dir)
