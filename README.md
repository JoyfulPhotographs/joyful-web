# Joyful Photography Website

A professional photography portfolio website with responsive design, tabbed galleries, and contact form integration.

## Table of Contents
- [Setup Requirements](#setup-requirements)
- [Local Development Environment](#local-development-environment)
- [Image Management](#image-management)
  - [Option 1: Local Images](#option-1-local-images)
  - [Option 2: Amazon S3 Images](#option-2-amazon-s3-images)
- [Website Configuration](#website-configuration)
- [Gallery Management](#gallery-management)
- [Contact Form Setup](#contact-form-setup)
- [Previewing and Testing](#previewing-and-testing)
- [Deployment](#deployment)

## Setup Requirements

### Required Software (Windows)

1. **Git** - For version control
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - During installation, choose the option to add Git to your PATH

2. **Visual Studio Code** - For editing website files
   - Download from [code.visualstudio.com](https://code.visualstudio.com/)
   - Recommended extensions:
     - Live Server (for local preview)
     - HTML CSS Support
     - Prettier - Code formatter

3. **Node.js** - For running local server and scripts
   - Download from [nodejs.org](https://nodejs.org/)
   - Install the LTS version

4. **Image Editing Software** (optional)
   - [GIMP](https://www.gimp.org/) (free)
   - [Adobe Photoshop](https://www.adobe.com/products/photoshop.html) (paid)
   - [Affinity Photo](https://affinity.serif.com/en-gb/photo/) (one-time purchase)

### Optional Software

1. **AWS CLI** - If using Amazon S3 for image hosting
   - Download from [aws.amazon.com/cli](https://aws.amazon.com/cli/)
   
2. **GitHub Desktop** - For easier Git operations
   - Download from [desktop.github.com](https://desktop.github.com/)

## Local Development Environment

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/joyful-web.git
   cd joyful-web
   ```

2. **Install http-server:**
   ```
   npm install -g http-server
   ```

3. **Start the local server:**
   ```
   cd docs
   http-server
   ```

4. **View the website:**
   - Open a browser and go to `http://localhost:8080` or the URL shown in your terminal

## Image Management

### Option 1: Local Images

1. **Image Directory Structure:**
   ```
   docs/
   └── images/
       ├── website/featured-nature.jpg     (used for landscapes)
       ├── website/featured-animal.jpg     (used for portraits/wildlife)
       ├── website/featured-city.jpg       (used for street photography)
       ├── website/featured-food.jpg       (miscellaneous)
       └── website/featured-architecture.jpg (miscellaneous)
   ```

2. **Preparing Images:**
   - For best performance, resize your images before uploading
   - Recommended dimensions:
     - Hero images: 1600px × 900px
     - Gallery thumbnails: 400px × 300px
   - Use JPG format for photos (PNG for graphics if needed)
   - Optimize file sizes using your image editor's export settings

3. **Adding New Images:**
   - Save your prepared images in the `docs/images/` directory
   - Update the references in `config.js` or `gallery-data.json` (see below)

### Option 2: Amazon S3 Images

1. **Setup Amazon S3:**
   - Create an AWS account if you don't have one
   - Create an S3 bucket with public read access
   - Configure CORS settings for your bucket

   **Secure AWS Credentials Setup:**
   - Create an IAM user with restricted permissions:
     ```json
     {
         "Version": "2012-10-17",
         "Statement": [
             {
                 "Effect": "Allow",
                 "Action": [
                     "s3:ListBucket",
                     "s3:GetObject",
                     "s3:PutObject",
                     "s3:PutObjectAcl"
                 ],
                 "Resource": [
                     "arn:aws:s3:::photos-joyfulphotographs-com",
                     "arn:aws:s3:::photos-joyfulphotographs-com/website-images/*"
                 ]
             }
         ]
     }
     ```
   - Configure AWS CLI locally (credentials stay on your machine, not in the repo):
     ```powershell
     # Install AWS CLI if needed
     # winget install -e --id Amazon.AWSCLI
     
     # Configure a named profile
     aws configure --profile joyful-photos
     ```
   - Enter your access key, secret key, region (e.g., us-east-1), and output format (json)

2. **Using the S3 Sync Script:**
   A PowerShell script named `sync-images.ps1` is included in the root folder of this repository to help you sync images between your local directory and an Amazon S3 bucket.
   
   To use it:
   
   - Edit the script and update the S3 bucket name in the `$S3_BUCKET` variable
   - Open PowerShell
   - Navigate to your repository root directory
   - Run the script: `./sync-images.ps1`
   
   The script will:
   - First download any images from S3 to your local `docs/images` directory
   - Ask if you want to upload local images to S3
   - If you choose to upload, it generates a text file with all the S3 URLs for easy reference

3. **Using S3 Images in the Website:**
   - The website is configured to use images from the S3 bucket with a centralized configuration
   - The S3 bucket and prefix are defined once in `config.js`:
     ```javascript
     s3: {
       bucketUrl: 'https://photos-joyfulphotographs-com.s3.amazonaws.com',
       prefix: 'website-images',
       getImageUrl: function(imagePath) {
         return `${this.bucketUrl}/${this.prefix}/${imagePath}`;
       }
     }
     ```
   - All image paths in both `config.js` and `gallery-data.json` use simple relative paths:
     ```javascript
     homepageImages: {
       hero: 'website/featured-nature.jpg',
       // other images...
     }
     ```
   - The helper function `siteConfig.s3.getImageUrl()` is used to build the full URLs when needed

## Website Configuration

### Configuration Files

#### config.js

The `docs/js/config.js` file contains site-wide configuration settings:

- **S3 Configuration**: Central bucket URL and prefix configuration with helper function
- **Image paths**: Relative paths for homepage and other site-wide images
- **Color scheme**: Variables for consistent site-wide styling
- **Form IDs**: Formspree form ID for the contact form

1. **Open `docs/js/config.js` in your editor**

2. **Homepage Images:**
   ```javascript
   homepageImages: {
     hero: 'images/website/featured-nature.jpg',  // Hero banner image
     featured: {
       portrait: 'images/website/featured-animal.jpg',
       landscape: 'images/website/featured-nature.jpg',
       wildlife: 'images/website/featured-animal.jpg',
       street: 'images/website/featured-city.jpg'
     }
   }
   ```

3. **Site Images:**
   ```javascript
   siteImages: {
     logo: 'images/logo.jpg',
     aboutHero: 'images/website/featured-architecture.jpg',
     contactBanner: 'images/website/featured-city.jpg'
   }
   ```

4. **Color Scheme:**
   ```javascript
   colors: {
     primary: '#333333',   // Main color
     accent: '#007acc',    // Highlight color
     light: '#f5f5f5',     // Light background
     dark: '#212121',      // Dark background
     text: '#333333',      // Body text
     textLight: '#ffffff'  // Light text (for dark backgrounds)
   }
   ```

## Gallery Management

The photo galleries are managed through `docs/gallery-data.json`.

### Gallery Structure
         "images": [
           {
             "src": "images/website/featured-nature.jpg",
             "alt": "Ballet dancers in motion",
             "description": "Grace and precision in every movement."
           },
           // More images...
         ]
       },
       // More categories...
     ]
   }
   ```

2. **Adding/Editing Categories:**
   - Each category needs a unique `id` (URL-friendly, lowercase)
   - Provide a display `name` and `description`
   
3. **Managing Gallery Images:**
   - Each image needs a `src` (path to image file)
   - Include `alt` text for accessibility 
   - Optionally add a `description` that appears with the image

4. **Gallery Validation Tool:**
   - A validation script ensures consistency between gallery data and actual images
   - Run it manually with:
     ```powershell
     # Validate gallery against local images
     ./validate-gallery.ps1

     # Validate gallery against S3 images
     ./validate-gallery.ps1 -UseS3

     # Run silently (only shows errors)
     ./validate-gallery.ps1 -Quiet
     ```
   - The validation tool checks:
     * All images referenced in gallery-data.json exist in the images folder/S3
     * All images in the images folder/S3 are referenced in gallery-data.json
     * The gallery-data.json file is valid JSON
   - A Git pre-commit hook automatically runs this validation when you change gallery-data.json

## Contact Form Setup

The contact form is integrated with Formspree:

1. **Create a Formspree account:**
   - Visit [formspree.io](https://formspree.io) and sign up
   - Create a new form
   - Copy your form ID (looks like "xyyzbba")

2. **Update config.js with your Formspree ID:**
   ```javascript
   forms: {
     contactFormId: 'YOUR_FORM_ID_HERE'
   }
   ```

## Previewing and Testing

1. **Start local server:**
   ```
   cd docs
   http-server
   ```

2. **Test in multiple browsers:**
   - Chrome
   - Firefox
   - Edge
   
3. **Test responsive design:**
   - Use browser developer tools to test different screen sizes
   - Firefox/Chrome: Press F12, then click the responsive design mode icon

4. **Test contact form:**
   - Submit a test message via the contact form
   - Check your email for the submission
   
## Deployment

1. **Commit your changes:**
   ```
   git add .
   git commit -m "Updated website content"
   git push
   ```

2. **Deploy to GitHub Pages:**
   - Go to your GitHub repository settings
   - Navigate to "Pages" section
   - Set source to the `docs` folder on your main branch
   - Click "Save"
   
3. **Custom Domain (Optional):**
   - Add your domain in the GitHub Pages settings
   - Create required DNS records with your domain provider
   - Enable HTTPS once DNS propagation is complete

4. **Verify Deployment:**
   - Check that your site is accessible at the GitHub Pages URL
   - Test all functionality on the live site
