<template>
    <header>
      <nav class="navbar navbar-expand-lg fixed-top shadow bg-white" :class="isDarkmode ? 'navbar-dark dark-theme' : 'navbar'">
        <div class="container-fluid">
          <a class="navbar-brand" href="/">Yaad</a>
          <button
            class="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav me-auto">
              <li class="nav-item">
                <RouterLink to="/" class="nav-link" :class="{ active: $route.path === '/' }">Home</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :class="{ active: $route.path === '/index' }" to="/index">Index</RouterLink>
              </li>
              <li class="nav-item" v-if="!currentUser">
                <RouterLink class="nav-link" :class="{ active: $route.path === '/signup' }" to="/signup">Get Started</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :class="{ active: $route.path === '/dashboard' }" to="/dashboard">Dashboard</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :class="{ active: $route.path === '/investment-tools' }" to="/investment-tools">Investment Tools</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :class="{ active: $route.path === '/price-evaluator' }" to="/price-evaluator">Price Evaluator</RouterLink>
              </li>
              <li class="nav-item" v-if="!currentUser">
                <RouterLink class="nav-link" :class="{ active: $route.path === '/login' }" to="/login">Login</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :class="{ active: $route.path === '/signout' }" to="/signout">Sign Out</RouterLink>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </header>
  </template>
  
  <script setup>
  import { RouterLink } from "vue-router";
  import { currentUser } from '@/assets/js/auth.js'; 
  import { defineProps } from 'vue';
  
  /**
   * Props for the AppHeader component.
   * 
   * @property {Boolean} isDarkmode - Indicates whether the dark mode is enabled.
   */
  const props = defineProps({
    isDarkmode: Boolean
  });
  </script>
  
  <style>
  .dark-theme {
    background-color: #1f2a3a !important; /* Dark mode */
  }

  .navbar:not(.dark-theme) .nav-link {
    color: black !important;
  }

  .dark-theme .nav-link {
    color: #fff !important;
  }

  .nav-link:hover {
    color: #ffcc00b4 !important;
  }

  .nav-link.active {
    color: #ffcc00 !important;
  }
</style>
