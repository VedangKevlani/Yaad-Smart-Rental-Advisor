<script setup>
import { ref } from 'vue';
import { auth } from '@/assets/js/firebase.js'; // your firebase config file
import { signInWithEmailAndPassword } from 'firebase/auth';
import { useRouter } from 'vue-router';
import { currentUser } from '@/assets/js/auth.js';

const router = useRouter();

const email = ref('');
const password = ref('');
const errorMsg = ref('');
const successMsg = ref('');

const flashMessage = (prompt) => {
    setTimeout(() => {
        prompt.value = '';
  }, 2000);
}

const isValidEmail = (email) => {
  // Simple email regex
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

const login = async () => {
  errorMsg.value = '';
  successMsg.value = '';

  if (!isValidEmail(email.value)) {
    errorMsg.value = 'Please enter a valid email address!!';
    flashMessage(errorMsg);
    return;
  } else {
    try {

        await signInWithEmailAndPassword(auth, email.value.trim(), password.value.trim());

        email.value = '';
        password.value = '';

        successMsg.value = 'Login successful!!';
        flashMessage(successMsg);

        setTimeout(() => {
            router.push('/'); 
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

  flashMessage(errorMsg);
}

}
};
</script>

<template>
<div class="d-flex justify-content-center align-items-center vh-100">
    <div class="card p-4 shadow-lg login-container">
    <img class="home-icon" src="../img/yaadlogo.jpg" alt="Yaad logo"><h2>Login to Yaad.</h2>

    <transition name="fade">
        <div v-if="successMsg || errorMsg" :class="successMsg ? 'success-message' : 'error-message'">
            {{ successMsg || errorMsg }}
        </div>
    </transition>


    <form @submit.prevent="login">
      <div class="form-group">
        <label for="email">Email Address</label>
        <input type="email" id="email" placeholder="Enter your email" v-model="email" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" placeholder="Enter your password" v-model="password" required />
      </div>
      <div class="form-group">
        <button type="submit" class="submit-button" href="index.html">Sign In <span class="chevron-icon">➔</span></button>
      </div>
    </form>
    <p class="footer-text">
      Don't have an account?
      <router-link to="/signup">Sign up</router-link>
    </p>
  </div>
  </div>
</template>

<style scoped>
.success-message {
    color: green;
    background-color: #d4edda;
    padding: 10px;
    border-radius: 5px;
    width: 40%;
    top: 115px;
    right: 15px;
    text-align: center;
    position: absolute;
    z-index: 10;
}

.error-message {
    color: red;
    background-color: #f8d7da;
    padding: 10px;
    border-radius: 5px;
    width: 60%;
    top: 115px;
    right: 15px;
    text-align: center;
    position: absolute;
    z-index: 10;
}

.fade-leave-active {
  transition: opacity 1s ease-in-out;
}

.fade-leave-to {
  opacity: 0;
}
</style>