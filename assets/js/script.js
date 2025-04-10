document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('dark-mode-toggle');
  const body = document.body;
  const form = document.querySelector('.property-form');
  const toast = document.getElementById('toast');  // Ensure this is at the top level

  // Toggle dark mode
  toggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    toggle.textContent = body.classList.contains('dark-mode') ? '☀️ Light Mode' : '🌙 Dark Mode';
  });

  // Show toast message
  function showToast(message, type = 'success') {
    const toastContent = toast.querySelector('.toast-content');  // Accessing the toast content element
    if (toastContent) {  // Ensure toastContent is not null
      toastContent.textContent = message;
      toast.className = 'toast show ' + type;
      setTimeout(() => {
        toast.className = 'toast';
      }, 3000);
    }
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const fullName = document.getElementById('full-name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (!fullName || !email || !password || !confirmPassword) {
      showToast("Please fill in all fields.", "error");
      return;
    }

    if (password !== confirmPassword) {
      showToast("Passwords do not match.", "error");
      return;
    }

    // Retrieve existing users from localStorage (or initialize empty array)
    let users = JSON.parse(localStorage.getItem('users')) || [];

    // Add the new user
    const newUser = {
      fullName,
      email,
      password 
    };

    users.push(newUser); // Add new user to the array

    // Save the updated list of users
    localStorage.setItem('users', JSON.stringify(users));

    showToast("Signed up successfully!", "success");

    // Redirect after a delay
    setTimeout(() => {
      window.location.href = 'home.html';
    }, 2000);
  });
});
