document.addEventListener('DOMContentLoaded', () => {
  const galleryContainer = document.getElementById('gallery-container');

  if (galleryContainer) {
    fetch('../gallery-data.json') // Assumes gallery.html is in docs/ and gallery-data.json is in docs/
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.length === 0) {
          galleryContainer.innerHTML = '<p>No images to display at the moment. Check back soon!</p>';
          return;
        }
        
        // Create gallery items from the data
        data.forEach(item => {
          const galleryItem = document.createElement('div');
          galleryItem.classList.add('gallery-item'); // Required for Masonry
          
          const img = document.createElement('img');
          img.src = item.src;
          img.alt = item.alt;
          
          const description = document.createElement('p');
          description.classList.add('gallery-item-description');
          description.textContent = item.description;

          galleryItem.appendChild(img);
          galleryItem.appendChild(description);
          galleryContainer.appendChild(galleryItem);
        });
        
        // Initialize Masonry after all images are loaded
        // This ensures proper layout calculation based on actual image dimensions
        const msnry = new Masonry(galleryContainer, {
          itemSelector: '.gallery-item',
          columnWidth: '.gallery-item',
          percentPosition: true,
          gutter: 10 // Space between items
        });
        
        // Use imagesLoaded to recalculate layout after all images have loaded
        imagesLoaded(galleryContainer).on('progress', () => {
          // Layout gets refreshed each time an image loads
          msnry.layout();
        });
      })
      .catch(error => {
        console.error('Error fetching or processing gallery data:', error);
        galleryContainer.innerHTML = '<p>Sorry, something went wrong while loading the gallery. Please try again later.</p>';
      });
  } else {
    // If you have multiple pages, it's normal for this to not be found on some.
    // console.warn('Gallery container #gallery-container not found on this page.');
  }
});
