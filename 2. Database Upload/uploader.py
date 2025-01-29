import os
import cloudinary
import cloudinary.uploader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Cloudinary with your credentials
cloudinary.config(
    cloud_name="dtux4mmyq",  # Replace with your Cloudinary cloud name
    api_key="299462445711338",  # Replace with your API key
    api_secret="ltquAoyIgRoiwTWL7wxERSQbRNU",  # Replace with your API secret
    secure=True
)

# Function to upload a single image to Cloudinary
def upload_image(image_path, folder):
    file_name = os.path.splitext(os.path.basename(image_path))[0]
    try:
        result = cloudinary.uploader.upload(
            image_path,
            folder=folder,
            public_id=file_name
        )
        logging.info(f"Uploaded: {result['secure_url']}")
        return result
    except Exception as e:
        logging.error(f"Failed to upload {image_path}: {e}")
        return None

# Upload images from a specific folder
def upload_images_from_folder(folder_path, cloud_folder):
    try:
        files = os.listdir(folder_path)
        logging.info(f"Files in folder: {files}")

        # Filter only image files
        image_files = [f for f in files if os.path.splitext(f)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif']]

        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            logging.info(f"Uploading: {image_file} to Cloudinary folder: {cloud_folder}")

            result = upload_image(image_path, cloud_folder)
            if result:
                logging.info(f"Uploaded: {result['secure_url']}")
            else:
                logging.error(f"Failed to upload {image_file}")
    except Exception as e:
        logging.error(f"Error processing folder {folder_path}: {e}")

# Paths to the local folders containing your image datasets
folder_paths = {
    'C:/Users/ASUS/Desktop/BFSI_OCR_Bank/Webscraping/financial_data/bank_statements': 'financial_data/bank_statements',
    'C:/Users/ASUS/Desktop/BFSI_OCR_Bank/Webscraping/financial_data/cheques': 'financial_data/cheques',
    'C:/Users/ASUS/Desktop/BFSI_OCR_Bank/Webscraping/financial_data/profit_loss_statements': 'financial_data/profit_loss_statements',
    'C:/Users/ASUS/Desktop/BFSI_OCR_Bank/Webscraping/financial_data/salary_slips': 'financial_data/salary_slips',
    'C:/Users/ASUS/Desktop/BFSI_OCR_Bank/Webscraping/financial_data/transaction_history': 'financial_data/transaction_history',
}

# Start uploading the images to the corresponding Cloudinary folders
for local_folder, cloud_folder in folder_paths.items():
    upload_images_from_folder(local_folder, cloud_folder)
