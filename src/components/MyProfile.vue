<script setup>
import { collection, query, where, getDocs } from 'firebase/firestore';
import { db } from '@/assets/js/firebase.js';
import { ref, onMounted, nextTick } from 'vue';
import { currentUser } from '@/assets/js/auth.js';

const userID = localStorage.getItem('userID');
const queries = ref([]);


async function getPriceEvaluatorQueries() {
  const price_evaluator_queries = query(collection(db, 'price-evaluator-queries'), where('uid', '==', userID));
  const query_result = await getDocs(price_evaluator_queries);

  query_result.forEach((doc) => {
    queries.value.push(doc.data());
  });

}

onMounted(() => {
  getPriceEvaluatorQueries();
});



</script>

<template>
  <div class="main-body" v-if="currentUser">
    <div class="profile-header">
      <p id="name">{{ currentUser.displayName }}</p>
      <p id="email">{{ currentUser.email }}</p>
    </div>

    <h2>Previous Price Evaluator Queries</h2>

    <div class="price-evaluator-queries">
      <details class="query" v-for="(query, index) in queries" :key="query.id || index">
        <summary>
          Query {{ index + 1 }} - {{ query.square_footage.toLocaleString() }} sq ft, ${{ query.predicted_value.toLocaleString() }}
        </summary>

        <div class="option">
          <label for="square_footage">Square Footage:</label>
          <p>{{ query.square_footage.toLocaleString() }} sq ft</p>
        </div>

        <div class="option">
          <label for="bedrooms">Bedrooms:</label>
          <p>{{ query.bedrooms }}</p>
        </div>

        <div class="option">
          <label for="bathrooms">Bathrooms:</label>
          <p>{{ query.bathrooms }}</p>
        </div>

        <div class="option">
          <label for="monthly_rent">Monthly Rent:</label>
          <p>${{ query.monthly_rent.toLocaleString() }}.00</p>
        </div>

        <div class="option">
          <label for="24_hour_security">24 Hour Security?</label>
          <p>{{ query.security_24hr }}</p>
        </div>

        <div class="option">
          <label for="swimming_pool">Swimming Pool?</label>
          <p>{{ query.swimming_pool }}</p>
        </div>

        <div class="option">
          <label for="view_ocean">Ocean View?</label>
          <p>{{ query.view_ocean }}</p>
        </div>

        <div class="option">
          <label for="waterfront_ocean">Waterfront?</label>
          <p>{{ query.waterfront_ocean }}</p>
        </div>

        <div class="option">
          <label for="garden_area">Garden Area?</label>
          <p>{{ query.garden_area }}</p>
        </div>

        <div class="option">
          <label for="central_location">Central Location?</label>
          <p>{{ query.central_location }}</p>
        </div>

        <div class="option">
          <label for="gated_community">Gated Community?</label>
          <p>{{ query.gated_community }}</p>
        </div>

        <div class="option">
          <label for="furnished">Furnished?</label>
          <p>{{ query.furnished }}</p>
        </div>

        <div class="option">
          <label for="predicted_value">Predicted Value:</label>
          <p>${{ query.predicted_value.toLocaleString() }}</p>
        </div>
      </details>
    </div>
  </div>
</template>

<style scoped>
.main-body {
  padding: 2rem;
  max-width: 100%;
  height: 100%;
  min-height: 1000px;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
}

.price-evaluator-queries {
  width: 100%;
  align-items: start;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 70px 40px;
  margin-top: 30px;
  margin-left: 190px;
}

.query {
  width: 60%;
  height: auto;
  border: 1px solid #ccc;
  border-radius: 10px;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: left;
  justify-content: center;
  transition: all 0.3s ease-in-out;
  padding: 1rem;
}

.query:hover {
  transform: scale(1.05);
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
}

.dark-mode .query {
  background-color: #0f172a;
  border: #0f172a;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.9);
}

.option {
  display: flex;
  flex-direction: row;
}

.option label {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-right: 10px;
}

.option p {
  font-size: 16px;
  font-weight: 400;
  color: #333;
}

.dark-mode .option * {
  color: white;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  margin-bottom: 2rem;
  width: 20%;
  padding: 1rem;

  border: 1px solid #ccc;
  border-radius: 10px;

  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  transform: perspective(800px) rotateX(5deg);
  transform-style: preserve-3d;
  transition: all 0.3s ease-in-out;
}

.dark-mode .profile-header {
  border: #0f172a;
  background-color: #0f172a;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.9);
}

.dark-mode #name,
#email {
  color: white;
}

#name {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

#email {
  font-size: 14px;
  font-weight: 400;
  color: #666;
}

.query summary {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  outline: none;
}

.query[open] {
  background-color: #f9f9f9;
}

.dark-mode .query[open] {
  background-color: #1e293b;
}
</style>
