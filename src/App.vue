<script setup>
import { RouterLink, RouterView } from 'vue-router'
import AppHeader from "@/components/AppHeader.vue";
import AppFooter from "@/components/AppFooter.vue";
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';

const transitionName = ref('fade');
const router = useRouter();

router.afterEach((to, from) => {
  if (from.name === 'login' && to.name === 'signup') {
    transitionName.value = 'slide-left';
  } else if (from.name === 'login' && to.name === 'index') {
    transitionName.value = 'fade';
  } else if (from.name === 'signup' && to.name === 'login') {
    transitionName.value = 'slide-right';
  } else if (from.name === 'home' && to.name === 'signup') {
    transitionName.value = 'slide-left';
  } else if (from.name === 'home' && to.name === 'login') {
    transitionName.value = 'slide-left';
  } else if (from.name === 'index' && to.name === 'investment-tools') {
    transitionName.value = 'slide-left';
  } else if (from.name === 'investment-tools' && to.name === 'index') {
    transitionName.value = 'slide-right';
  } else if (from.name === 'investment-tools' && to.name === 'my-profile') {
    transitionName.value = 'slide-left';
  } else if (from.name === 'my-profile' && to.name === 'investment-tools') {
    transitionName.value = 'slide-right';
  } else if (from.name === 'index' && to.name === 'my-profile') {
    transitionName.value = 'slide-left';
  } else if (from.name === 'my-profile' && to.name === 'index') {
    transitionName.value = 'slide-right';
  } else {
    transitionName.value = 'fade';
  }
})
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
  if (isDarkmode.value) {
    document.body.classList.add('dark-mode');
    document.body.classList.remove('light-mode');
  } else {
    document.body.classList.remove('dark-mode');
    document.body.classList.add('light-mode');
  }
};
</script>

<template>
  <AppHeader :isDarkmode="isDarkmode" />
  
  <button class="btn nav-button" :class="themeClass" @click="toggleTheme">
    {{ buttonText }}
  </button>

  <main style="position: relative; min-height: 100vh;">
    <RouterView v-slot="{ Component }">
      <transition :name="transitionName" mode="out-in">
        <component :is="Component" :isDarkmode="isDarkmode" />
      </transition>
    </RouterView>


  </main>

  <AppFooter :isDarkmode="isDarkmode" />
</template>


<style>
.btn.nav-button {
  text-decoration: none;
  font-size: 16px;
  top: 70px;
  right: 10px;
  position: absolute;
  background-color: gray;
  color: #fff;
  border-color: gray;
  z-index: 10;
}

.btn.nav-button:hover {
  background-color: black;
  color: #fff;
  border-color: black;
}

body {
  padding-top: 75px;
  position: relative;
  transition: background-color 0.5s ease, color 0.5s ease;
}

body.dark-mode {
  background: linear-gradient(to bottom right, #1e293b, #0f172a);
  color: #f8fafc;
  transition: background-color 0.5s ease, color 0.5s ease;
}

body.light-mode {
  background-color: #fff;
  color: black;
  transition: background-color 0.5s ease, color 0.5s ease;
}

/* Fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
}

/* Slide Left */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.4s ease;
  position: absolute;
  width: 100%;
}

.slide-left-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-left-enter-to {
  transform: translateX(0);
  opacity: 1;
}

.slide-left-leave-from {
  transform: translateX(0);
  opacity: 1;
}

.slide-left-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

/* Slide Right */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.4s ease;
  position: absolute;
  width: 100%;
}

.slide-right-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-right-enter-to {
  transform: translateX(0);
  opacity: 1;
}

.slide-right-leave-from {
  transform: translateX(0);
  opacity: 1;
}

.slide-right-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>