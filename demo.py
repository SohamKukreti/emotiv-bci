import os
import requests

# Create a directory called 'assets' if it doesn't exist
output_dir = "assets"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to download an image
def download_image(image_url, file_path):
    try:
        # Send GET request to download the image
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        # Write the content of the image to the specified file path
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {file_path}")
    except requests.RequestException as e:
        print(f"Error downloading {image_url}: {e}")

# Function to generate image URLs and download them
def download_images(num_images=100):
    for i in range(1, num_images + 1):
        # Generate a random square image URL from the Picsum API (200x200)
        image_url = f"https://picsum.photos/200?random={i}"  # Ensure a different random image each time
        # Define the path where the image will be saved
        file_path = os.path.join(output_dir, f"image_{i}.jpg")
        # Download the image
        download_image(image_url, file_path)

# Download 100 square images
download_images(100)
