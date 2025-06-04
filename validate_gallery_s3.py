import os
import sys
import json

# Attempt to set up logging as the VERY FIRST operation
LOG_FILE_PATH = '' # Initialize
ABS_SCRIPT_DIR = '' # Initialize
try:
    ABS_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__) if '__file__' in locals() else os.getcwd())
    LOG_FILE_PATH = os.path.join(ABS_SCRIPT_DIR, 'debug_validate_s3.log')
    with open(LOG_FILE_PATH, 'w', encoding='utf-8') as lf:
        lf.write("--- Log Start (validate_gallery_s3.py) ---\n")
        lf.write(f"Initial log path: {LOG_FILE_PATH}\n")
        lf.write(f"ABS_SCRIPT_DIR: {ABS_SCRIPT_DIR}\n")
except Exception as e:
    print(f"CRITICAL: Failed to initialize logging for validate_gallery_s3.py: {e}", file=sys.stderr)

def log_message(message, level='INFO'):
    formatted_message = f"{level}: {message}\n"
    if level == 'ERROR':
        print(formatted_message.strip(), file=sys.stderr)
    else:
        print(formatted_message.strip(), file=sys.stdout)
    if LOG_FILE_PATH:
        try:
            with open(LOG_FILE_PATH, 'a', encoding='utf-8') as lf:
                lf.write(formatted_message)
        except Exception as e:
            print(f"ERROR: Failed to write to log file {LOG_FILE_PATH}: {e}", file=sys.stderr)

# Proceed with other imports AFTER basic logging is attempted
try:
    import requests # For HTTP HEAD requests
    log_message("Successfully imported 'requests' library.", level='DEBUG')
except ImportError as e:
    log_message(f"Failed to import 'requests': {e}. Please ensure it is installed ('pip install requests').", level='ERROR')
    sys.exit(1)
except Exception as e:
    log_message(f"An unexpected error occurred during imports: {e}", level='ERROR')
    sys.exit(1)

log_message(f"DEBUG: __file__ = {__file__ if '__file__' in locals() else 'not_defined'}", level='DEBUG')
log_message(f"DEBUG: ABS_SCRIPT_DIR = {ABS_SCRIPT_DIR}", level='DEBUG')

# Configuration
GALLERY_DATA_FILE = os.path.join(ABS_SCRIPT_DIR, 'docs', 'gallery-data.json')
log_message(f"DEBUG: GALLERY_DATA_FILE = {GALLERY_DATA_FILE}", level='DEBUG')
S3_BUCKET_NAME = "photos-joyfulphotographs-com"
S3_PREFIX = "website-images/"
# Construct the base URL for S3 objects. Adjust if your region or URL format is different.
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/"

def print_error(message):
    log_message(message, level='ERROR')

def print_success(message):
    log_message(message, level='SUCCESS')

def print_info(message):
    log_message(message, level='INFO')

def check_s3_image_exists(image_relative_path):
    """Checks if an image exists in S3 using an HTTP HEAD request."""
    s3_key = os.path.join(S3_PREFIX, image_relative_path).replace("\\", "/")
    image_url = S3_BASE_URL + s3_key
    
    try:
        response = requests.head(image_url, timeout=5) # 5 second timeout
        if response.status_code == 200:
            # print_info(f"Found in S3: {image_relative_path} (URL: {image_url})")
            return True
        else:
            # print_error(f"Missing in S3 (HTTP {response.status_code}): {image_relative_path} (URL: {image_url})")
            return False
    except requests.exceptions.RequestException as e:
        # print_error(f"HTTP request failed for {image_relative_path} (URL: {image_url}): {e}")
        return False

def main():
    print_info("Starting S3 gallery validation...")
    errors_found = 0

    # 1. Check gallery-data.json exists and is valid JSON
    print_info(f"Checking gallery-data.json at {GALLERY_DATA_FILE}")
    if not os.path.exists(GALLERY_DATA_FILE):
        print_error(f"gallery-data.json not found at {GALLERY_DATA_FILE}")
        sys.exit(1)

    try:
        with open(GALLERY_DATA_FILE, 'r', encoding='utf-8') as f:
            gallery_data = json.load(f)
        print_success("gallery-data.json is valid JSON")
    except json.JSONDecodeError as e:
        print_error(f"gallery-data.json is not valid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Could not read gallery-data.json: {e}")
        sys.exit(1)

    # 2. Validate image references in gallery_data.json against S3
    image_references_count = 0
    missing_in_s3_count = 0

    if 'categories' not in gallery_data or not isinstance(gallery_data['categories'], list):
        print_error("'categories' key missing or not a list in gallery-data.json")
        sys.exit(1)

    print_info(f"Validating image references against S3 bucket: {S3_BUCKET_NAME}/{S3_PREFIX}")
    for category in gallery_data.get('categories', []):
        if 'images' not in category or not isinstance(category['images'], list):
            # This should ideally be caught by local validation first
            print_error(f"Category '{category.get('name', 'N/A')}' missing 'images' list.")
            errors_found +=1 # Count as a structural error too
            continue
        for item in category.get('images', []):
            if 'src' not in item:
                print_error(f"Image item in category '{category.get('name')}' missing 'src' key: {item}")
                errors_found += 1
                continue
            
            image_src = item['src'] # e.g., "gallery/sample-nature.jpg"
            image_references_count += 1
            
            if not check_s3_image_exists(image_src):
                print_error(f"Missing in S3: {image_src}")
                missing_in_s3_count += 1
    
    print_info(f"Checked {image_references_count} image references against S3.")
    errors_found += missing_in_s3_count

    if errors_found == 0:
        print_success("All S3 validations passed! All referenced images found in S3.")
        sys.exit(0)
    else:
        if missing_in_s3_count > 0:
            print_error(f"{missing_in_s3_count} images are referenced in JSON but missing from S3.")
        if errors_found > missing_in_s3_count:
             print_error("Additional structural errors found in gallery-data.json during S3 validation.")
        print_error(f"S3 validation failed with a total of {errors_found} errors.")
        sys.exit(1)

if __name__ == "__main__":
    log_message("This script uses the 'requests' library. If not installed, run: pip install requests", level='INFO')
    main()
