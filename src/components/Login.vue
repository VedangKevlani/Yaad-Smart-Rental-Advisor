<script setup>
import { ref } from 'vue';
import { auth } from '@/assets/js/firebase.js';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { useRouter } from 'vue-router';
import { currentUser } from '@/assets/js/auth.js';

const router = useRouter();

const email = ref('');
const password = ref('');
const errorMsg = ref('');
const successMsg = ref('');


const isValidEmail = (email) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

function showToast(message, type) {
  const toast = document.querySelector("#toast");
  const toastContent = toast.querySelector(".toast-content");

  if (!toast || !toastContent) {
    console.error("Toast element or content not found.");
    return;
  }

  toastContent.textContent = message;
  toast.classList.add("show", type);

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

const login = async () => {
  errorMsg.value = '';
  successMsg.value = '';

  if (!isValidEmail(email.value)) {
    errorMsg.value = 'Please enter a valid email address!!';
    showToast(errorMsg.value, "error");
    return;
  } else {
    try {

      await signInWithEmailAndPassword(auth, email.value.trim(), password.value.trim());

      localStorage.setItem('userID', currentUser.value.uid);

      email.value = '';
      password.value = '';

      successMsg.value = 'Login successful!!';
      showToast(successMsg.value, "success");

      setTimeout(() => {
        router.push('/index');
      }, 4000);
    } catch (error) {
      console.error("Firebase auth error:", error.code, error.message);

      if (error.code === 'auth/wrong-password') {
        errorMsg.value = 'Incorrect password!!';
      } else if (error.code === 'auth/user-not-found') {
        errorMsg.value = 'User not found!!';
      } else if (error.code === 'auth/invalid-email') {
        errorMsg.value = 'Invalid email!!';
      } else if (error.code === 'auth/invalid-credential') {
        errorMsg.value = 'Invalid email or password!!';
      } else {
        errorMsg.value = 'Login failed. Please try again.';
      }
      showToast(errorMsg.value, "error");
    }
  }
};
</script>

<template>
  <div class="login-root">
    <div class="d-flex justify-content-center align-items-center vh-100">
      <div class="card p-4 shadow-lg login-container">
        <img class="home-icon" src="../img/yaadlogo.jpg" alt="Yaad logo">
        <h2>Login to Yaad.</h2>

        <form @submit.prevent="login"  autocomplete="off">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input type="email" id="email" placeholder="Enter your email" v-model="email"  autocomplete="off"/>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" placeholder="Enter your password" v-model="password" autocomplete="off"/>
          </div>
          <div class="form-group">
            <button type="submit" class="submit-button">Sign In <span
                class="chevron-icon">➔</span></button>
          </div>
        </form>
        <p class="footer-text">
          Don't have an account?
          <router-link to="/signup">Sign up</router-link>
        </p>
      </div>
    </div>
    <div id="toast" class="toast">
      <div class="toast-content"></div>
    </div>
  </div>
</template>
