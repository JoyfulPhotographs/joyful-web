document.addEventListener('DOMContentLoaded', () => {
  const galleryContainer = document.getElementById('gallery-container');
  const tabsContainer = document.getElementById('gallery-tabs');
  const categoryHeading = document.getElementById('category-heading');
  const categoryDescription = document.getElementById('category-description');

  if (galleryContainer) {
    fetch('../gallery-data.json') // Assumes gallery.html is in docs/ and gallery-data.json is in docs/
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (!data.categories || data.categories.length === 0) {
          galleryContainer.innerHTML = '<p>No gallery categories found. Please check back later.</p>';
          return;
        }
        
        // Function to create and initialize Masonry
        const initMasonry = () => {
          // Clear any existing Masonry instance
          if (galleryContainer.masonry) {
            galleryContainer.masonry.destroy();
          }
          
          // Initialize new Masonry instance
          const msnry = new Masonry(galleryContainer, {
            itemSelector: '.gallery-item',
            percentPosition: true,
            gutter: 10
          });
          
          // Store the Masonry instance on the container
          galleryContainer.masonry = msnry;
          
          // Use imagesLoaded to recalculate layout after all images have loaded
          imagesLoaded(galleryContainer).on('progress', () => {
            msnry.layout();
          });
        };
        
        // Function to display a category's images
        const displayCategory = (categoryId) => {
          // Find the selected category
          const category = data.categories.find(cat => cat.id === categoryId);
          if (!category) return;
          
          // Update active tab
          const tabs = tabsContainer.querySelectorAll('.tab');
          tabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.category === categoryId);
          });
          
          // Clear gallery container
          galleryContainer.innerHTML = '';
          
          // Update category heading and description if they exist
          if (categoryHeading) categoryHeading.textContent = category.name;
          if (categoryDescription) categoryDescription.textContent = category.description;
          
          // If no images in this category
          if (!category.images || category.images.length === 0) {
            galleryContainer.innerHTML = `<p>No images available in the ${category.name} category yet.</p>`;
            return;
          }
          
          // Add images to gallery
          category.images.forEach(item => {
            const galleryItem = document.createElement('div');
            galleryItem.classList.add('gallery-item');
            
            const img = document.createElement('img');
            // Use the S3 helper function to build the full URL from the relative path
            img.src = siteConfig.s3.getImageUrl(item.src);
            img.alt = item.alt;
            img.loading = 'lazy'; // Lazy loading for better performance
            
            const description = document.createElement('p');
            description.classList.add('gallery-item-description');
            description.textContent = item.description;
            
            galleryItem.appendChild(img);
            galleryItem.appendChild(description);
            galleryContainer.appendChild(galleryItem);
          });
          
          // Initialize Masonry after adding all items
          initMasonry();
        };
        
        // Create tabs for each category
        if (tabsContainer) {
          // Clear any existing tabs
          tabsContainer.innerHTML = '';
          
          // Create tabs
          data.categories.forEach(category => {
            const tab = document.createElement('button');
            tab.classList.add('tab');
            tab.dataset.category = category.id;
            tab.textContent = category.name;
            
            tab.addEventListener('click', () => {
              displayCategory(category.id);
            });
            
            tabsContainer.appendChild(tab);
          });
          
          // Display first category by default
          if (data.categories.length > 0) {
            const firstTab = tabsContainer.querySelector('.tab');
            firstTab.classList.add('active');
            displayCategory(data.categories[0].id);
          }
        }
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
