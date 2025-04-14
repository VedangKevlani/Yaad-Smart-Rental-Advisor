document.addEventListener('DOMContentLoaded', () => {
  const propertyImageInput = document.getElementById('propertyImage');
  const resultDiv = document.getElementById('result');
  const spinner = document.getElementById('spinner');
  const propertyForm = document.getElementById('propertyForm');
  const toast = document.getElementById('toast');

  function showToast(message, type = 'success') {
    const toastContent = document.querySelector('.toast-content');
    toastContent.textContent = message;
    toast.className = 'toast show ' + type;
    setTimeout(() => {
      toast.className = 'toast';
    }, 3000);
  }

  propertyForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    const address = document.getElementById('address').value;
    const bedrooms = document.getElementById('bedrooms').value || 'Not specified';
    const bathrooms = document.getElementById('bathrooms').value || 'Not specified';
    const squareFeet = document.getElementById('squareFeet').value || 'Not specified';
    const rentCost = document.getElementById('rentCost').value || 'Not specified';
    const imageFile = propertyImageInput.files[0] || null;

    if (!address) {
      showToast('Please enter a property address to analyze.', 'error');
      return;
    }

    if (imageFile) {
      const formData = new FormData();
      formData.append('image', imageFile);
      spinner.style.display = 'block';

      try {
        const response = await fetch('http://127.0.0.1:3000/check-image', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Image check failed. Status: ${response.status}`);
        }

        const data = await response.json();

        if (data.message && data.message.toLowerCase().includes('ai-generated')) {
          showToast('Image appears to be AI-generated. Please use a real property image.', 'error');
          spinner.style.display = 'none';
          return;
        }
      } catch (error) {
        showToast(`Error analyzing image: ${error.message}`, 'error');
        spinner.style.display = 'none';
        return;
      } finally {
        spinner.style.display = 'none';
      }
    }

    showToast('We\'re analyzing your property');

    const formData = {
      address,
      bedrooms,
      bathrooms,
      squareFeet,
      rentCost,
      imageFileName: imageFile ? imageFile.name : 'No image uploaded'
    };

    localStorage.setItem('submittedProperty', JSON.stringify(formData));
    window.location.href = 'dashboard.html';
  });

  const fadeElements = document.querySelectorAll('.fade-in');
  fadeElements.forEach(el => {
    setTimeout(() => {
      el.style.opacity = 1;
    }, 100);
  });
});
