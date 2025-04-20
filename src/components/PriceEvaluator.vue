<!-- components/PriceEvaluator.vue -->
<template>
    <div class="popup-overlay" @click.self="$emit('close')">
      <div class="popup-content">
        <h5>💲 Price Evaluator</h5>
        <p>Insert your evaluator form or logic here.</p>
        <!-- X icon for closing the popup -->
        <button class="close-btn" @click="$emit('close')">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const price = ref(null);
  const evaluatePrice = () => {
    // Logic for price evaluation goes here
    console.log("Evaluating price:", price.value);
  };
  </script>
  
  <style scoped>
  .popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1100;
    animation: fadeIn 0.3s ease-out;
  }
  
  .popup-content {
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    padding: 2rem;
    border-radius: 12px;
    width: 400px;
    max-width: 90%;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    position: relative;
    animation: scaleUp 0.3s ease-out;
  }
  
  h5 {
    color: #333;
    font-size: 1.5rem;
    margin-bottom: 1rem;
  }
  
  p {
    color: #555;
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
  }
  
  .btn-primary {
    background-color: #007bff;
    border-color: #007bff;
    padding: 0.75rem 1.5rem;
    font-size: 1.1rem;
    border-radius: 25px;
    width: 100%;
    transition: background-color 0.3s ease;
  }
  
  .btn-primary:hover {
    background-color: #0056b3;
    border-color: #004085;
  }
  
  .close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 1.75rem;
    color: #555;
    cursor: pointer;
    transition: color 0.3s ease, transform 0.3s ease;
  }
  
  .close-btn:hover {
    color: #d9534f;
    transform: scale(1.2);
  }
  
  .close-btn i {
    font-size: 1.75rem;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
  
  @keyframes scaleUp {
    from {
      transform: scale(0.9);
    }
    to {
      transform: scale(1);
    }
  }
  </style>