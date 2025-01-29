import os
from bing_image_downloader import downloader
import shutil
from PIL import Image
import cv2

class ImageDownloader:
    def __init__(self):
        pass

    def quality_check(self, image_path):
        try:
            # Using Pillow library for a basic check
            img = Image.open(image_path)
            img.verify()  # Verify image integrity

            # Using OpenCV for blur detection (Laplacian variance)
            img_cv = cv2.imread(image_path)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            if variance > 200:  # Example threshold, adjust as needed
                return True  # Image is likely sharp
            else:
                return False  # Image is likely blurry
        except Exception as e:  # Catch any image processing errors
            print(f"Error checking image {image_path}: {e}")
            return False

    def fetch_bing_images(self):
        # Create category folders for image downloads
        categories = ["salary_slips", "bank_statements", "cheques", "profit_loss_statements", "transaction_history"]
        for category in categories:
            os.makedirs(f"financial_data/{category}", exist_ok=True)

        # Define search terms for each category
        search_terms = {
            "salary_slips": "salary slip document",
            "bank_statements": "bank statement document",
            "cheques": "cheques document",
            "profit_loss_statements": "profit and loss statements",
            "transaction_history": "transaction history document"
        }

        # Download images for each search term
        for category, term in search_terms.items():
            print(f"Downloading images for: {term}")
            downloader.download(term, limit=150,
                                output_dir=f"financial_data/{category}",
                                adult_filter_off=True,
                                force_replace=False,
                                timeout=60)

            # Dynamically find the correct folder
            temp_folder = os.path.join(f"financial_data/{category}", term)
            if not os.path.exists(temp_folder):
                print(f"No folder found for {term}. Skipping...")
                continue

            image_counter = 1
            for filename in os.listdir(temp_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    source = os.path.join(temp_folder, filename)
                    destination = os.path.join(f"financial_data/{category}", f"image{image_counter}.jpg")

                    if self.quality_check(source):  # Quality check before moving
                        shutil.move(source, destination)
                        image_counter += 1
                    else:
                        print(f"Skipping blurry image: {source}")
                        os.remove(source)  # Remove the blurry image

            shutil.rmtree(temp_folder)  # Clean up temp folder
            print(f"Finished processing images for: {term}")

        print("Images downloaded and organized successfully")

if __name__ == "__main__":
    image_downloader = ImageDownloader()
    image_downloader.fetch_bing_images()
