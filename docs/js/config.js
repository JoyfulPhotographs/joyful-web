/**
 * Site-wide configuration file for Joyful Photography
 * All shared resources like image paths and colors are defined here
 */
const siteConfig = {
  // S3 configuration
  s3: {
    bucketUrl: 'https://photos-joyfulphotographs-com.s3.amazonaws.com',
    prefix: 'website-images',
    // Helper function to build full S3 URLs
    getImageUrl: function(imagePath) {
      // Check if we're running on localhost - use local images for development
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return `/images/${imagePath}`;
      }
      // Otherwise use S3 for production
      return `${this.bucketUrl}/${this.prefix}/${imagePath}`;
    }
  },
  
  // Homepage images (relative paths - s3.getImageUrl will be used to construct full URLs)
  homepageImages: {
    hero: 'website/featured-nature.jpg',
    featured: {
      portrait: 'website/featured-animal.jpg',
      landscape: 'website/featured-nature.jpg',
      wildlife: 'website/featured-animal.jpg',
      street: 'website/featured-city.jpg'
    }
  },
  
  // General site images (non-gallery)
  siteImages: {
    logo: 'logo.jpg',
    aboutHero: 'website/featured-architecture.jpg',
    contactBanner: 'website/featured-city.jpg'
  },
  
  // Color scheme
  colors: {
    primary: '#333333',
    accent: '#007acc',
    light: '#f5f5f5',
    dark: '#212121',
    text: '#333333',
    textLight: '#ffffff'
  },
  
  // Form settings
  forms: {
    // Replace this with your actual Formspree form ID when you create one at https://formspree.io/
    contactFormId: 'xdkzkaad' // julia form ID
  }
};
