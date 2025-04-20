<script setup>
import { RouterLink, RouterView } from 'vue-router'
import AppHeader from "@/components/AppHeader.vue";
import AppFooter from "@/components/AppFooter.vue";
import { ref, computed, onMounted } from 'vue';



/* - `isDarkmode`: A boolean prop that determines whether the application is in dark mode. */
const isDarkmode = ref(false);

// Load preference from localStorage on page load
onMounted(() => {
  const saved = localStorage.getItem('theme');
  isDarkmode.value = saved === 'dark';
  updateThemeClass();
});

// Computed class for button
const themeClass = computed(() => (isDarkmode.value ? 'dark' : 'light'));

// Computed text for button
const buttonText = computed(() =>
  isDarkmode.value ? '🌞' : '🌙'
);

// Method to toggle theme
const toggleTheme = () => {
  isDarkmode.value = !isDarkmode.value;
  updateThemeClass();
  localStorage.setItem('theme', isDarkmode.value ? 'dark' : 'light');
};

// Apply theme class to body
const updateThemeClass = () => {
  if (isDarkmode.value){
      document.body.classList.add('dark-mode');
      document.body.classList.remove('light-mode');
  } else {
      document.body.classList.remove('dark-mode');
      document.body.classList.add('light-mode');
  }
};
</script>

<template>
  <!--
    This line renders the `AppHeader` component and passes a prop named `isDarkmode` to it.
  -->
  <AppHeader :isDarkmode="isDarkmode" />

  <main>
    <button class="btn nav-button" :class="themeClass" @click="toggleTheme">
    {{ buttonText }}
  </button>
    <RouterView :isDarkmode="isDarkmode" />
  </main>

  <AppFooter :isDarkmode="isDarkmode" />
</template>


<style>

body {
  padding-top: 75px;
  position: relative;
}

body.dark-mode {
  background: linear-gradient(to bottom right, #1e293b, #0f172a);
  color: #f8fafc;
}

body.light-mode {
    background-color: #fff;
    color: black;
}


</style>