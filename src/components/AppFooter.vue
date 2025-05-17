<template>
    <footer class="footer">
        <div class="container">
            <p>© {{ year }} Yaad: Smart Property Advisor. All rights reserved.</p>
        </div>
    </footer>
</template>

<script setup>
import { ref } from "vue";

const year = (new Date).getFullYear();
</script>

<style scoped>

.footer {
  text-align: center;
  font-family: "Georgia", "Times New Roman", serif;
}

.container {
  width: 100%;
  display: flex;
  justify-content: center;
  margin: 0 auto;
}

.container-light-mode {
color: black;
}

.container-dark-mode {
color: #d4d4d4;
}

p {
font-family: "Georgia", "Times New Roman", serif;
bottom: 0px;
position: absolute;
}
</style>




