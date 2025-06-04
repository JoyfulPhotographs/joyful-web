import json
import os
import sys

LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'debug_validate_local.log')

# Clear log file at start
with open(LOG_FILE_PATH, 'w', encoding='utf-8') as lf:
    lf.write("--- Log Start ---\n")

def log_message(message, level='INFO'):
    formatted_message = f"{level}: {message}\n"
    # Also print to original stdout/stderr for good measure
    if level == 'ERROR':
        print(formatted_message.strip(), file=sys.stderr)
    else:
        print(formatted_message.strip(), file=sys.stdout)
    with open(LOG_FILE_PATH, 'a', encoding='utf-8') as lf:
        lf.write(formatted_message)

# --- BEGIN EARLY DEBUG PRINTS ---
log_message(f"__file__ = {__file__}", level='DEBUG')
SCRIPT_DIR = os.path.dirname(__file__)
log_message(f"SCRIPT_DIR (os.path.dirname(__file__)) = {SCRIPT_DIR}", level='DEBUG')
ABS_SCRIPT_DIR = os.path.abspath(SCRIPT_DIR)
log_message(f"ABS_SCRIPT_DIR (os.path.abspath(SCRIPT_DIR)) = {ABS_SCRIPT_DIR}", level='DEBUG')
# --- END EARLY DEBUG PRINTS ---

CONFIG_FILE = os.path.join(ABS_SCRIPT_DIR, 'docs', 'js', 'config.js')
log_message(f"CONFIG_FILE set to: {CONFIG_FILE}", level='DEBUG')
GALLERY_DATA_FILE = os.path.join(ABS_SCRIPT_DIR, 'docs', 'gallery-data.json')
log_message(f"GALLERY_DATA_FILE set to: {GALLERY_DATA_FILE}", level='DEBUG')
LOCAL_IMAGE_BASE_PATH = os.path.join(ABS_SCRIPT_DIR, 'docs', 'images')
log_message(f"LOCAL_IMAGE_BASE_PATH set to: {LOCAL_IMAGE_BASE_PATH}", level='DEBUG')
LOCAL_GALLERY_IMAGE_PATH = os.path.join(LOCAL_IMAGE_BASE_PATH, 'gallery')
log_message(f"LOCAL_GALLERY_IMAGE_PATH set to: {LOCAL_GALLERY_IMAGE_PATH}", level='DEBUG')

def print_error(message):
    log_message(message, level='ERROR')

def print_success(message):
    log_message(message, level='SUCCESS')

def print_info(message):
    log_message(message, level='INFO')

def main():
    print_info("Starting local gallery validation...")
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

    # 2. Validate image references in gallery_data.json against local files
    referenced_images = set()
    image_references_count = 0

    if 'categories' not in gallery_data or not isinstance(gallery_data['categories'], list):
        print_error("'categories' key missing or not a list in gallery-data.json")
        sys.exit(1)

    for category in gallery_data.get('categories', []):
        if 'images' not in category or not isinstance(category['images'], list):
            print_error(f"Category '{category.get('name', 'N/A')}' missing 'images' list.")
            errors_found +=1
            continue
        for item in category.get('images', []):
            if 'src' not in item:
                print_error(f"Image item in category '{category.get('name')}' missing 'src' key: {item}")
                errors_found += 1
                continue
            
            image_src = item['src']
            image_references_count += 1
            referenced_images.add(image_src) # Store relative path as in JSON
            
            # Construct full local path. Assuming 'src' is relative to 'docs/images/'
            # e.g., if src is 'gallery/myimage.jpg', full path is 'docs/images/gallery/myimage.jpg'
            full_local_path = os.path.join(LOCAL_IMAGE_BASE_PATH, image_src.replace('/', os.sep))
            
            if not os.path.exists(full_local_path):
                print_error(f"Missing local file: {image_src} (Expected at {full_local_path})")
                errors_found += 1
    
    print_info(f"Found {image_references_count} image references in gallery-data.json")

    # 3. Check for unreferenced images in the local gallery folder
    print_info(f"Checking for unreferenced images in {LOCAL_GALLERY_IMAGE_PATH}...")
    if os.path.exists(LOCAL_GALLERY_IMAGE_PATH):
        local_gallery_files = set()
        for root, _, files in os.walk(LOCAL_GALLERY_IMAGE_PATH):
            for file_name in files:
                # Get path relative to LOCAL_IMAGE_BASE_PATH, matching format in referenced_images
                full_file_path = os.path.join(root, file_name)
                relative_to_base = os.path.relpath(full_file_path, LOCAL_IMAGE_BASE_PATH)
                local_gallery_files.add(relative_to_base.replace(os.sep, '/'))

        unreferenced_files = local_gallery_files - referenced_images
        if unreferenced_files:
            print_error(f"Found {len(unreferenced_files)} unreferenced images in {LOCAL_GALLERY_IMAGE_PATH}:")
            for unreferenced_file in unreferenced_files:
                # Only report if it's in the 'gallery/' subdirectory as per original script logic
                if unreferenced_file.startswith('gallery/'):
                    print_error(f"  - {unreferenced_file}")
                    errors_found += 1
        else:
            print_success(f"No unreferenced images found in {LOCAL_GALLERY_IMAGE_PATH}.")
    else:
        print_info(f"Local gallery image path {LOCAL_GALLERY_IMAGE_PATH} does not exist. Skipping unreferenced check.")

    if errors_found == 0:
        print_success("All local validations passed!")
        sys.exit(0)
    else:
        print_error(f"Local validation failed with {errors_found} errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()
