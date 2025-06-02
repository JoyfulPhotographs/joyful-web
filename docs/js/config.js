/**
 * Site-wide configuration file for Joyful Photography
 * All shared resources like image paths and colors are defined here
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
    // Replace this with your actual Formspree form ID when you create one at https://formspree.io/
    contactFormId: 'mdkzoddy' // Example ID - replace with your actual Formspree form ID
  }
};
