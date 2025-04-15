<template>
    
  </template>
  
  <script setup>
  import { onMounted } from 'vue';
  import { useRouter } from 'vue-router'; 
  import { logout } from '@/auth'; 
  
  const router = useRouter(); 
  
  onMounted(async () => {
    try {
      await logout(); 
      router.push('/'); 
    } catch (error) {
      console.error('Error logging out:', error);
    }
  });
  </script>
  