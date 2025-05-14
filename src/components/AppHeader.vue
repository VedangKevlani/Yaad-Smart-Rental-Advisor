<template>
  <header>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    <nav class="navbar navbar-expand-lg fixed-top shadow bg-white" :class="isDarkmode ? 'navbar-dark dark-theme' : 'navbar'">
      <div class="container-fluid d-flex justify-content-between align-items-center">
        <a class="navbar-brand d-flex align-items-center gap-2" href="/">
  <img src="src\assets\img\trans_logo.png" alt="App Logo" style="height: 30px; width: auto;" />
  <span style="color: white;">Yaad</span>
</a>


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

        <div class="collapse navbar-collapse justify-content-end" id="navbarSupportedContent">
          <ul class="navbar-nav">
            <li class="nav-item" v-if="currentUser">
              <RouterLink class="nav-link" :class="{ active: $route.path === '/index' }" to="/index">Analyze Property</RouterLink>
            </li>
            <li class="nav-item" v-if="currentUser">
              <RouterLink class="nav-link" :class="{ active: $route.path === '/investment-tools' }" to="/investment-tools">Investment Tools</RouterLink>
            </li>
            <li class="nav-item" v-if="currentUser">
              <RouterLink class="nav-link d-flex align-items-center gap-2" :class="{ active: $route.path === '/my-profile' }" to="/my-profile">
                <i class="bi bi-person-circle"></i>My Profile 
              </RouterLink>
            </li>
            <li class="nav-item" v-if="!currentUser">
              <RouterLink class="nav-link" :class="{ active: $route.path === '/login'}" to="/login">Login</RouterLink>
            </li>
            <li class="nav-item" v-if="currentUser">
              <RouterLink class="nav-link" :class="{ active: $route.path === '/signout'}" to="/signout">Sign Out</RouterLink>
            </li>
            <li class="nav-item" v-if="!currentUser">
              <RouterLink class="nav-link" :class="{ active: $route.path === '/signup'}" to="/signup">Sign Up</RouterLink>
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

const props = defineProps({
  isDarkmode: Boolean
});
</script>

<style>

.navbar:not(.dark-theme) {
  background-color: #48b5d0 !important;
}

.navbar:not(.dark-theme) .nav-link {
  color: white !important;
}

.dark-theme .nav-link {
  color: #fff !important;
}

.navbar-dark.dark-theme {
  background-color: #1f2a3a !important;
}

.nav-link{
  color: #fff !important;
}

.nav-link:hover {
  color: #ffcc00b4 !important;
}

.nav-link.active {
  color: #ffcc00 !important;
}

</style>
