<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { auth, db } from '@/assets/js/firebase.js';
import { createUserWithEmailAndPassword, updateProfile } from 'firebase/auth';
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';

const router = useRouter();

const name = ref('');
const email = ref('');
const password = ref('');
const c_password = ref('');
const successMsg = ref('');
const errorMsg = ref('');

const flashMessage = (prompt) => {
  setTimeout(() => {
    prompt.value = '';
  }, 2000);
};

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

const register = async () => {
  if (!isValidEmail(email.value)) {
    errorMsg.value = 'Please enter a valid email address!!';
    showToast(errorMsg.value, "error");
    return;
  } else if (password.value.length < 6) {
    errorMsg.value = 'Password should be at least 6 characters!!';
    showToast(errorMsg.value, "error");
    return;
  }else if (password.value !== c_password.value) {
    errorMsg.value = 'Passwords do not match!!';
    showToast(errorMsg.value, "error");
    return;
  }  else {
    try {
      const userCredentials = await createUserWithEmailAndPassword(auth, email.value, password.value);
      const user = userCredentials?.user;


      if (!user) {
        errorMsg.value = 'Registration failed: no user returned!!';
        showToast(errorMsg.value, "error");
        return;
      }

      await updateProfile(user, { displayName: name.value });

      await setDoc(doc(db, 'users', user.uid), {
        name: name.value,
        email: email.value,
        password: password.value,
        uid: user.uid,
        createdAt: serverTimestamp(),
      });

      name.value = '';
      email.value = '';
      password.value = '';
      c_password.value = '';

      successMsg.value = 'User registered!!';
      showToast(successMsg.value, "success");

      setTimeout(() => {
        router.push('/login');
      }, 2000);
    } catch (err) {
      errorMsg.value = err.message;
      showToast(errorMsg.value, "error");
    }
  }
};
</script>

<template>
  <div class="sign-up-root">
    <div class="container">
      <section class="hero fade-in">
        <div class="hero-content slide-up">
          <div class="logo-title">
            <img src="../img/yaadlogo.jpg" alt="Yaad Logo" class="home-icon" />
            <h1 class="title">Yaad<span class="highlight">.</span></h1>
          </div>
          <p class="subtitle">Find Your Perfect Rental with AI</p>
          <p class="description">Sign up to explore AI-optimized property listings and get insights tailored for you in
            Kingston & St. Andrew.</p>
        </div>

        <div class="form-container slide-up">
          <form class="property-form" @submit.prevent="register">
            <div class="form-group">
              <label class="label-with-icon" for="full-name">Full Name</label>
              <input type="text" id="full-name" class="input-field" placeholder="John Doe" v-model="name"
                autocomplete="off" />
            </div>

            <div class="form-group">
              <label class="label-with-icon" for="email">Email Address</label>
              <input type="text" id="email" class="input-field" placeholder="you@example.com" v-model="email"
                autocomplete="off" />
            </div>

            <div class="form-group">
              <label class="label-with-icon" for="password">Password</label>
              <input type="password" id="password" class="input-field" placeholder="••••••••" v-model="password"
                autocomplete="off" />
            </div>

            <div class="form-group">
              <label class="label-with-icon" for="confirm-password">Confirm Password</label>
              <input type="password" id="confirm-password" class="input-field" placeholder="••••••••"
                v-model="c_password" autocomplete="off" />
            </div>

            <div class="form-group">
              <button type="submit" class="submit-button">
                Create Account
                <span class="chevron-icon">➔</span>
              </button>
            </div>
          </form>
        </div>
      </section>
    </div>
    <div id="toast" class="toast">
      <div class="toast-content"></div>
    </div>
  </div>
</template>

<style scoped></style>
