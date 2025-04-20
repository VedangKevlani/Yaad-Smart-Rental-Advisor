<script setup>
import { useRouter } from 'vue-router';
import { currentUser } from '@/assets/js/auth.js';

const router = useRouter()

const signUp = () => {
  router.push('/signup').then(() => {
    window.scrollTo(0, 0);
  });
}
</script>

<template>
  <section class="landing-content fade-in">
    <div class="hero slide-up">
      <div>
        <h1 class="title">Find Your Perfect Rental in Kingston</h1>
        <p class="subtitle">Smart. Fast. AI-Powered. Let Yaad analyze listings so you don’t have to.</p>
        <a href="#signup" class="nav-button signup" style="margin-top: 1rem;">Start Now</a>
      </div>
      <img src="../img/jamhome.jpg" alt="Apartment Image" class="hero-image">
    </div>

    <div class="features" id="features">
      <div class="feature-box slide-up">
        <div class="feature-icon">🏙️</div>
        <h3>Smart Detection</h3>
        <p>Upload a screenshot of a listing — Yaad uses AI to detect key features instantly.</p>
      </div>
      <div class="feature-box slide-up">
        <div class="feature-icon">📊</div>
        <h3>Location Analytics</h3>
        <p>See maps, crime stats, commute times, and more. Make informed decisions effortlessly.</p>
      </div>
      <div class="feature-box slide-up">
        <div class="feature-icon">💬</div>
        <h3>Chat with Yaad</h3>
        <p>Ask questions like “Is this listing safe?” or “Can I afford this?” and get instant answers.</p>
      </div>
    </div>

    <div class="cta-section slide-up" id="signup">
      <h2>Ready to Find Your Dream Rental?</h2>
      <p>Sign up and start analyzing listings with the power of AI.</p>
      <button class="cta-button" @click="signUp">Create an Account</button>
    </div>
  </section>
</template>

<style scoped>

</style>