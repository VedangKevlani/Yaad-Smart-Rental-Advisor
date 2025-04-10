document.addEventListener('DOMContentLoaded', () => {
  const checkImageButton = document.getElementById('checkImage');
  const propertyImageInput = document.getElementById('propertyImage');
  const resultDiv = document.getElementById('result');
  const spinner = document.getElementById('spinner');

  checkImageButton.addEventListener('click', async (event) => {
    // Prevent default form submission behavior, which might cause the page to reload
    event.preventDefault();

    const imageFile = propertyImageInput.files[0];
    if (!imageFile) {
      alert('Please select an image');
      return;
    }

    // Show loading spinner
    spinner.style.display = 'block';

    // Create FormData and append the image file
    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      // Send image to the backend
      const response = await fetch('http://127.0.0.1:3000/check-image', {
        method: 'POST',
        body: formData,
      });

      // Handle HTTP errors (non-2xx status codes)
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log(data);

      // Display the result from the model
      if (data.message) {
        resultDiv.textContent = `Result: ${data.message}`;
      } else {
        resultDiv.textContent = 'No result returned from model.';
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      resultDiv.textContent = `An error occurred: ${error.message}`;
    } finally {
      // Hide spinner
      spinner.style.display = 'none';
    }
  });
});
