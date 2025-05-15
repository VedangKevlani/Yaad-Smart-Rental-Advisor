<script setup>
import { RouterLink, RouterView } from 'vue-router'
import AppHeader from "@/components/AppHeader.vue";
import AppFooter from "@/components/AppFooter.vue";
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const transitionName = ref('fade')
const router = useRouter()
const showNewComponent = ref(false)
const currentComponent = ref(null)
const route = useRoute();

router.afterEach((to, from) => {
  if (from.name === 'login' && to.name === 'signup') {
    transitionName.value = 'slide-left'
  } else if (from.name === 'login' && to.name === 'index') {
    transitionName.value = 'fade'
  } else if (from.name === 'signup' && to.name === 'login') {
    transitionName.value = 'slide-right'
  } else {
    transitionName.value = 'fade'
  }
})

const isShowingNew = ref(true)

router.beforeEach((to, from, next) => {
  isShowingNew.value = false
  setTimeout(() => {
    isShowingNew.value = true
  }, 20)
  next()
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
  <AppHeader :isDarkmode="isDarkmode" />

  <main>
    <button class="btn nav-button" :class="themeClass" @click="toggleTheme">
    {{ buttonText }}
  </button>
  

  <RouterView v-slot="{ Component }">
    <transition :name="transitionName" mode="out-in">
      <!-- key is important to force transitions -->
      <component :is="Component" :key="$route.fullPath" />
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

.component-old {
  position: absolute;
  width: 100%;
  top: 0;
  left: 0;
  z-index: 1;
}

.component-new {
  position: absolute;
  width: 100%;
  top: 0;
  left: 0;
  z-index: 2;
}


/* Fade */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from, .fade-leave-to { opacity: 0; }
.fade-enter-to, .fade-leave-from { opacity: 1; }

/* Slide Left */
.slide-left-enter-active, .slide-left-leave-active {
  transition: all 0.4s ease;
  position: absolute;
  width: 100%;
}
.slide-left-enter-from {
  transform: translateX(100%);
  opacity: 1;
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
  opacity: 1;
}

/* Slide Right */
.slide-right-enter-active, .slide-right-leave-active {
  transition: all 0.4s ease;
  position: absolute;
  width: 100%;
}
.slide-right-enter-from {
  transform: translateX(-100%);
  opacity: 1;
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
  opacity: 1;
}


</style>