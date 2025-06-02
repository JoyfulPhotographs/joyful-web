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
    hero: 'images/sample-nature.jpg',
    featured: {
      portrait: 'images/sample-animal.jpg',
      landscape: 'images/sample-nature.jpg',
      wildlife: 'images/sample-animal.jpg',
      street: 'images/sample-city.jpg'
    }
  },
  
  // General site images (non-gallery)
  siteImages: {
    logo: 'images/logo.jpg',
    aboutHero: 'images/sample-architecture.jpg',
    contactBanner: 'images/sample-city.jpg'
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
