/**
 * Site-wide configuration file for Joyful Photography
 * All shared resources like image paths and colors are defined here
 * 
 * INSTRUCTIONS:
 * 1. Copy this file and rename it to config.js
 * 2. Replace the dummy values with your actual values
 * 3. The actual config.js should not be committed to the repository
 */
const siteConfig = {
  // Homepage images
  homepageImages: {
    hero: 'images/website/featured-nature.jpg',
    featured: {
      portrait: 'images/website/featured-animal.jpg',
      landscape: 'images/website/featured-nature.jpg',
      wildlife: 'images/website/featured-animal.jpg',
      street: 'images/website/featured-city.jpg'
    }
  },
  
  // General site images (non-gallery)
  siteImages: {
    logo: 'images/logo.jpg',
    aboutHero: 'images/website/featured-architecture.jpg',
    contactBanner: 'images/website/featured-city.jpg'
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
    // Replace this with your actual Formspree form ID
    contactFormId: 'YOUR_FORMSPREE_ID_HERE'
  }
};
