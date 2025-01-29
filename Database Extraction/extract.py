import os
import requests
import cloudinary
import cloudinary.api
from dotenv import load_dotenv
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


def create_requests_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    """
    Create a requests session with retry capabilities
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def download_image(url, download_path, session=None):
    """
    Download image with improved error handling and retry mechanism
    """
    if session is None:
        session = requests.Session()

    try:
        response = session.get(url, timeout=(10, 30))  # (connect timeout, read timeout)

        if response.status_code == 200:
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            with open(download_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {download_path}")
            return True
        else:
            print(f"Failed to download image from {url}. Status code: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False


def fetch_and_download_images(folder_name, download_dir, max_retries=3):
    """
    Fetch and download images with improved error handling
    """
    session = create_requests_session()

    try:
        resources = cloudinary.api.resources(type="upload", prefix=folder_name, max_results=1000)

        if not resources.get('resources'):
            print(f"No resources found in the folder {folder_name}.")
            return

        os.makedirs(download_dir, exist_ok=True)

        total_images = len(resources['resources'])
        downloaded_images = 0
        failed_images = []

        for resource in resources['resources']:
            image_url = resource['secure_url']
            public_id = resource['public_id']

            local_path = public_id.replace(f'{folder_name}/', '')
            download_path = os.path.join(download_dir, f"{local_path}.jpg")

            success = False
            for attempt in range(max_retries):
                if download_image(image_url, download_path, session):
                    success = True
                    downloaded_images += 1
                    break
                time.sleep(2 ** attempt)  # Exponential backoff

            if not success:
                failed_images.append(image_url)
                print(f"Failed to download {image_url} after {max_retries} attempts")

            time.sleep(0.1)

        print(f"\nDownload Summary:")
        print(f"Total Images: {total_images}")
        print(f"Successfully Downloaded: {downloaded_images}")
        print(f"Failed Downloads: {len(failed_images)}")

        if failed_images:
            with open(os.path.join(download_dir, 'failed_downloads.txt'), 'w') as f:
                f.write("\n".join(failed_images))

    except Exception as e:
        print(f"Error fetching resources: {e}")


if __name__ == "__main__":
    folder_name = "financial_data"
    download_dir = "./downloaded_financial_data"

    fetch_and_download_images(folder_name, download_dir)
