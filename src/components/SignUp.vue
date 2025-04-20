<script setup>
import { ref } from 'vue';
import { auth, db } from '@/assets/js/firebase.js';
import { createUserWithEmailAndPassword, updateProfile } from 'firebase/auth';
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';
import { currentUser } from '@/assets/js/auth.js';

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
}

const isValidEmail = (email) => {
  // Simple email regex
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

const register = async () => {
    if (password.value !== c_password.value) {
    errorMsg.value = 'Passwords do not match!!';
    flashMessage(errorMsg);
    return;
  }else if (password.value.length < 6) {
    errorMsg.value = 'Password should be at least 6 characters!!';
    flashMessage(errorMsg);
    return;
  } else if (!isValidEmail(email.value)) {
    errorMsg.value = 'Please enter a valid email address!!';
    flashMessage(errorMsg);
    return;
  } else {
    try {
    const userCredentials = await createUserWithEmailAndPassword(auth, email.value, password.value);

    const user = userCredentials?.user;

    if (!user) {
      errorMsg.value = 'Registration failed: no user returned!!';
      flashMessage(errorMsg);
      return;
    }

    await updateProfile(user, { displayName: name.value })

    await setDoc(doc(db, 'users', user.uid), {
      name: name.value,
      email: email.value,
      password: password.value,
      uid: user.uid,
      createdAt: serverTimestamp(),
    });

    const token = await user.getIdToken();

    name.value = '';
    email.value = '';
    password.value = '';
    c_password.value = '';

    successMsg.value = 'User registered!!';
    flashMessage(successMsg);

    setTimeout(() => {
        router.push('/'); 
    }, 4000);
  } catch (err) {
    errorMsg.value = err.message;
  }
  }
  
};
</script>

<template>
    <div class="container">
        <section class="hero fade-in">
        <div class="hero-content slide-up">
            <div class="logo-title">
            <img src="../img/yaadlogo.jpg" alt="Yaad Logo" class="home-icon" />
            <h1 class="title">Yaad<span class="highlight">.</span></h1>
            </div>
            <p class="subtitle">Find Your Perfect Rental with AI</p>
            <p class="description">Sign up to explore AI-optimized property listings and get insights tailored for you in Kingston & St. Andrew.</p>
        </div>

        <transition name="fade">
            <div v-if="successMsg || errorMsg" :class="successMsg ? 'success-message' : 'error-message'">
                {{ successMsg || errorMsg }}
            </div>
        </transition>

        <div class="form-container slide-up">
            <form class="property-form" @submit.prevent="register">
            <div class="form-group">
                <label class="label-with-icon" for="full-name">Full Name</label>
                <input type="text" id="full-name" name="full-name" class="input-field" placeholder="John Doe" v-model="name" autocomplete=off required />
            </div>

            <div class="form-group">
                <label class="label-with-icon" for="email">Email Address</label>
                <input type="email" id="email" name="email" class="input-field" placeholder="you@example.com" v-model="email" autocomplete=off required />
            </div>

            <div class="form-group">
                <label class="label-with-icon" for="password">Password</label>
                <input type="password" id="password" name="password" class="input-field" placeholder="••••••••"  v-model="password" autocomplete=off required />
            </div>

            <div class="form-group">
                <label class="label-with-icon" for="confirm-password">Confirm Password</label>
                <input type="password" id="confirm-password" name="confirm-password" class="input-field" placeholder="••••••••" v-model="c_password"  autocomplete=off required />
            </div>

            <div class="form-group">
                <button type="submit" class="submit-button" href="index.html">
                Create Account
                <span class="chevron-icon">➔</span>
                </button>
            </div>
            </form>
        </div>
        </section>
  </div>
</template>

<style scoped>
.success-message {
    color: green;
    background-color: #d4edda;
    padding: 10px;
    border-radius: 5px;
    width: 20%;
    top: 370px;
    right: 120px;
    text-align: center;
    position: absolute;
    z-index: 10;
}

.error-message {
    color: red;
    background-color: #f8d7da;
    padding: 10px;
    border-radius: 5px;
    width: 20%;
    top: 370px;
    right: 120px;
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