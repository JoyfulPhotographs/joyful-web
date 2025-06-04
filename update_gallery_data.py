#!/usr/bin/env python
"""
Gallery Data JSON Updater Script

This script updates the gallery-data.json file based on the actual contents of the images/gallery folder
and its subfolders. It preserves existing alt text and descriptions while adding new images with
generated alt text and TODO descriptions.
"""

import os
import json
import re
from pathlib import Path

# Configuration
GALLERY_DATA_PATH = "docs/gallery-data.json"
GALLERY_IMAGES_PATH = "docs/images/gallery"
SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

def load_gallery_data():
    """Load the existing gallery data JSON file"""
    try:
        with open(GALLERY_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading gallery data: {e}")
        # Return a minimal structure if file doesn't exist or is invalid
        return {"categories": []}

def scan_gallery_folders():
    """Scan the gallery directory for subfolders (categories) and images"""
    gallery_structure = {}
    
    try:
        # Get all subdirectories in the gallery folder
        gallery_path = Path(GALLERY_IMAGES_PATH)
        if not gallery_path.exists():
            print(f"Gallery path not found: {gallery_path}")
            return gallery_structure
            
        # Map each subfolder to its image files
        for category_dir in [d for d in gallery_path.iterdir() if d.is_dir()]:
            category_name = category_dir.name
            gallery_structure[category_name] = []
            
            # Find all image files in this category
            for file_path in category_dir.glob("*"):
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    relative_path = f"gallery/{category_name}/{file_path.name}"
                    gallery_structure[category_name].append({
                        "file_name": file_path.name,
                        "relative_path": relative_path
                    })
                    
        return gallery_structure
    except Exception as e:
        print(f"Error scanning gallery folders: {e}")
        return {}

def generate_alt_text(file_name, category):
    """Generate alt text based on the filename and category"""
    # Remove file extension and replace underscores/hyphens with spaces
    name = os.path.splitext(file_name)[0]
    name = re.sub(r'[_-]', ' ', name)
    name = name.title()  # Capitalize first letter of each word
    
    return f"{name} - {category.title()} photography"

def update_gallery_json(existing_data, gallery_structure):
    """Update the gallery JSON data based on scanned folder structure"""
    # If gallery data is completely empty, initialize with basic structure
    if not existing_data.get("categories"):
        existing_data["categories"] = []
    
    # Create a lookup of existing images by their src path
    existing_images = {}
    for category in existing_data["categories"]:
        for img in category.get("images", []):
            if "src" in img:
                existing_images[img["src"]] = img
    
    # Create or update each category
    updated_categories = []
    
    for category_name, files in gallery_structure.items():
        # Look for existing category or create new one
        existing_category = None
        for category in existing_data["categories"]:
            if category.get("id", "").lower() == category_name.lower() or \
               category.get("name", "").lower() == category_name.lower():
                existing_category = category
                break
        
        if not existing_category:
            # Create new category
            title_name = category_name.replace('-', ' ').replace('_', ' ').title()
            existing_category = {
                "id": category_name,
                "name": title_name,
                "description": f"{title_name} photography collection", 
                "images": []
            }
        
        # Create a set of existing image paths in this category
        existing_category_srcs = {img.get("src") for img in existing_category.get("images", [])}
        
        # Update images for this category
        updated_images = []
        
        for file_info in files:
            relative_path = file_info["relative_path"]
            file_name = file_info["file_name"]
            
            # Check if this image already exists in the category
            if relative_path in existing_category_srcs:
                # Find and retain the existing image data
                for img in existing_category.get("images", []):
                    if img.get("src") == relative_path:
                        updated_images.append(img)
                        break
            elif relative_path in existing_images:
                # Image exists in another category, copy its metadata
                img = existing_images[relative_path].copy()
                img["src"] = relative_path  # Ensure path is correct
                updated_images.append(img)
            else:
                # New image, create entry with generated alt text
                # Omit description field by default for new images
                updated_images.append({
                    "src": relative_path,
                    "alt": generate_alt_text(file_name, category_name)
                })
        
        # Update the category with new images
        existing_category["images"] = updated_images
        updated_categories.append(existing_category)
    
    # Sort categories alphabetically by name
    updated_categories.sort(key=lambda x: x.get("name", ""))
    
    # Update the original data
    existing_data["categories"] = updated_categories
    return existing_data

def save_gallery_data(data):
    """Save the updated gallery data back to the JSON file"""
    try:
        with open(GALLERY_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Gallery data successfully updated at {GALLERY_DATA_PATH}")
        return True
    except Exception as e:
        print(f"Error saving gallery data: {e}")
        return False

def main():
    """Main script execution"""
    print("Starting gallery data update process...")
    
    # Load existing gallery data
    gallery_data = load_gallery_data()
    print(f"Loaded gallery data with {len(gallery_data.get('categories', []))} categories")
    
    # Scan gallery folders for image files
    gallery_structure = scan_gallery_folders()
    print(f"Found {len(gallery_structure)} gallery categories")
    
    # Update gallery JSON with new structure
    updated_data = update_gallery_json(gallery_data, gallery_structure)
    
    # Save updated gallery data
    success = save_gallery_data(updated_data)
    
    if success:
        print("Gallery data update complete!")
        # Print summary including info about images without captions
        images_without_captions = sum(1 for cat in updated_data["categories"] for img in cat.get("images", []) if "description" not in img)
        total_images = sum(len(cat.get("images", [])) for cat in updated_data["categories"])
        print(f"Updated {len(updated_data['categories'])} categories with {total_images} total images")
        print(f"Images without captions: {images_without_captions}")
        
        for category in updated_data["categories"]:
            print(f"  - {category.get('name', 'Unnamed')}: {len(category.get('images', []))} images")
    else:
        print("Gallery data update failed")

if __name__ == "__main__":
    main()
