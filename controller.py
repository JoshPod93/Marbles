import time
import twitch_chat
import os

# Set your image path and reference images directory
image_path = r'C:\Users\joshp\Desktop\Marbles\Images\Target\0001.png'
reference_images_dir = r'C:\Users\joshp\Desktop\Marbles\Images'

# Simulating a Twitch chat listener and continuous loop
def run():
    while True:
        # Simulate checking for new chat commands every 5 seconds
        time.sleep(5)

        # Example of a new chat command being received
        command = "!checkscreen"
        
        # Call the Twitch chat handler and get the response
        response = twitch_chat.handle_chat_command(command, image_path, reference_images_dir)
        
        # Simulate sending the response back to Twitch chat (this would use a Twitch API or bot)
        print("Twitch Response:", response)

# Run the main control loop
run()