<script setup>
import { ref, computed } from 'vue';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { db } from '@/assets/js/firebase.js';

defineProps({
  isDarkmode: Boolean,
});

const userID = localStorage.getItem('userID');

const result = ref(null);
const isLoading = ref(false);

const squareFeetInput = ref('');
const rentCostInput = ref('');

const form = ref({
  'Square Footage': '',
  Bedrooms: '',
  Bathrooms: '',
  EstimatedRent: '',
  '24_Hour_Security': 0,
  Furnished: 0,
  Garden_Area: 0,
  Swimming_Pool: 0,
  Central_Location: 0,
  Gated_Community: 0,
  'View_-_Ocean': 0,
  'Waterfront_-_Ocean': 0,
})

const binaryFeatures = [
  '24_Hour_Security',
  'Furnished',
  'Garden_Area',
  'Swimming_Pool',
  'Central_Location',
  'Gated_Community',
  'View_-_Ocean',
  'Waterfront_-_Ocean',
]

const formattedSquareFeet = computed(() => {
  const num = parseFloat(squareFeetInput.value.replace(/,/g, ''));
  if (isNaN(num)) return '';
  return `${num.toLocaleString()} sq ft`;
})

const updateSquareFeet = (val) => {
  squareFeetInput.value = val.replace(/[^\d.]/g, '');
  form.value['Square Footage'] = parseInt(squareFeetInput.value);
}

const formattedRentCost = computed(() => {
  const num = parseFloat(rentCostInput.value.replace(/,/g, ''));
  if (isNaN(num)) return '';
  return `$${num.toLocaleString()}`;
})

const updateRentCost = (val) => {
  rentCostInput.value = val.replace(/[^\d.]/g, '');
  form.value.EstimatedRent = parseFloat(rentCostInput.value);
}

const formatLabel = (label) => label.replace(/_/g, ' ').replace(/-/g, '–')

const verdictText = computed(() => {
  if (!result.value || !form.value['EstimatedRent']) return ''
  const predicted = result.value.predicted_value
  const actual = parseFloat(form.value['EstimatedRent'])
  const diffPercent = Math.abs(predicted - actual) / actual

  if (predicted > actual) {
    if (diffPercent >= 0.1) return '🤔 Underpriced. Be Cautious!'
    if (diffPercent >= 0.25) return '⚠️ Slightly Overestimated Rent'
    return '✅ Fair Price'
  } else if (predicted < actual) {
    if (diffPercent >= 0.1) return '🤔 Overpriced. Be Cautious!'
    if (diffPercent >= 0.25) return '❌ Significantly Overestimated Rent'
    return '✅ Great Deal'
  } else {
    return '🎯 Price is on Target'
  }
})

function showToast(message, type) {
  const toast = document.querySelector("#toast");
  const toastContent = toast.querySelector(".toast-content");

  toast.classList.remove("show", type);

  if (!toast || !toastContent) {
    console.error("Toast element or content not found.");
    return;
  }

  toastContent.textContent = message;
  toast.classList.add("show", type);

  setTimeout(() => {
    toast.classList.remove("show", type);
  }, 3000);
}

const evaluate = async () => {
  if (!form.value['Square Footage'] || !form.value.Bedrooms || !form.value.Bathrooms || !form.value.EstimatedRent) {
    showToast('Please fill in all the fields!!', 'error');
    return;
  }

  isLoading.value = true;
  result.value = null;

  const response = await fetch('http://localhost:5000/api/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value),
  })
  const data = await response.json()
  isLoading.value = false;


  if (data.predicted_value !== undefined) {
    await addDoc(collection(db, 'price-evaluator-queries'), {
      uid: userID,
      square_footage: form.value['Square Footage'] || 0,
      bedrooms: form.value.Bedrooms || 0,
      bathrooms: form.value.Bathrooms || 0,
      monthly_rent: form.value.EstimatedRent || 0,
      security_24hr: form.value['24_Hour_Security'] === 1 ? 'yes' : 'no',
      furnished: form.value.Furnished === 1 ? 'yes' : 'no',
      garden_area: form.value.Garden_Area === 1 ? 'yes' : 'no',
      swimming_pool: form.value.Swimming_Pool === 1 ? 'yes' : 'no',
      central_location: form.value.Central_Location === 1 ? 'yes' : 'no',
      gated_community: form.value.Gated_Community === 1 ? 'yes' : 'no',
      view_ocean: form.value['View_-_Ocean'] === 1 ? 'yes' : 'no',
      waterfront_ocean: form.value['Waterfront_-_Ocean'] === 1 ? 'yes' : 'no',
      predicted_value: data.predicted_value,
      createdAt: serverTimestamp(),
    });
    result.value = data
  } else {
    result.value = null
  }
}
</script>

<template>
  <div class="price-evaluator">
    <div class="popup-overlay" @click.self="$emit('close')">
      <div class="popup-content">
        <header class="popup-header">
          <h2 class="popup-title">💲 Price Evaluator</h2>
          <button @click="$emit('close')" class="popup-close-btn" aria-label="Close">&times;</button>
        </header>

        <p class="popup-description">
          Fill in the form to evaluate the rental price of your property by comparing expected rent to predicted rent.
        </p>
        <p class="location-info">(For Kingston & St. Andrew Apartments Only)</p>

        <div class="popup-form">
          <div class="form-group">
            <label for="squareFootage">Square Footage</label>
            <input type="text" :value="formattedSquareFeet" @input="updateSquareFeet($event.target.value)"
              id="squareFootage" class="form-control" />
          </div>
          <div class="form-group">
            <label for="bedrooms">Bedrooms</label>
            <input v-model="form.Bedrooms" type="number" id="bedrooms" class="form-control" />
          </div>
          <div class="form-group">
            <label for="bathrooms">Bathrooms</label>
            <input v-model="form.Bathrooms" type="number" id="bathrooms" class="form-control" />
          </div>
          <div class="form-group">
            <label for="estimatedRent">Monthly Rent</label>
            <input type="text" :value="formattedRentCost" @input="updateRentCost($event.target.value)"
              id="estimatedRent" class="form-control" />
          </div>

          <div class="form-group form-grid">
            <label v-for="feature in binaryFeatures" :key="feature" class="form-checkbox-label">
              <input v-model="form[feature]" type="checkbox" :true-value="1" :false-value="0" :id="feature"
                class="form-checkbox-input" />
              <span>{{ formatLabel(feature) }}</span>
            </label>
          </div>
        </div>

        <div class="popup-footer">

          <button @click="evaluate" class="submit-button">Evaluate</button>


          <div v-if="result" class="popup-result">
            <p class="result-predicted-value">
              Predicted Monthly Rent: ${{ result.predicted_value.toLocaleString() }}
            </p>
            <p class="result-verdict">
              {{ verdictText }}
            </p>
          </div>

          <div v-show="isLoading" ref="spinner" class="spinner-container">
            <div id="spinner" class="spinner"></div>
          </div>
        </div>
      </div>
    </div>
    <div id="toast" class="toast">
      <div class="toast-content"></div>
    </div>
  </div>
</template>



<style scoped>
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1100;
  overflow: auto;
}

.popup-content {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dark-mode .popup-content {
  background-color: #0f172a;
}

.dark-mode .popup-content * {
  color: white;
}

.toast {
  position: fixed;
  top: 120px;
  right: 30px;
  transform: translateX(120%);
  background-color: grey;
  color: var(--white);
  padding: 5px 10px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  transition: transform 0.3s ease;
  z-index: 1100;
  max-width: 400px;
  height: 40px;
  font-size: 16px;
  font-weight: bold;
  text-align: start;
  opacity: 1;
}

.dark-mode .toast {
  background-color: var(--dark);
  color: var(--white);
  border: none;
  box-shadow: var(--shadow);
}

.toast.show {
  transform: translateX(0);
}

.toast.error {
  border-left: 14px solid #ef4444;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.popup-title {
  font-size: 1.5rem;
  font-weight: bold;
}

.popup-close-btn {
  font-size: 2rem;
  background: none;
  border: none;
  cursor: pointer;
  position: absolute;
  top: 0;
  right: 0;
  padding: 0.5rem;
}

.popup-description {
  margin: 1rem 0;
  color: #555;
}

.popup-form {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-right: 4px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-control {
  padding: 0.75rem;
  font-size: 1rem;
  border-radius: 8px;
  border: 1px solid #ccc;
}

.location-info {
  font-size: 1rem;
  color: black;
  margin-top: 1rem;
  font-weight: 700;
  text-align: center;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.5rem;
}

.form-checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-checkbox-input {
  width: 1rem;
  height: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.popup-footer {
  margin-top: 1.5rem;
  text-align: center;
  justify-content: center;
}


.popup-result {
  margin-top: 1.5rem;
  font-size: 0.95rem;
  color: #444;
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.popup-close-btn {
  font-size: 2rem;
  background: none;
  border: none;
  cursor: pointer;
  position: absolute;
  top: 0;
  right: 0;
  padding: 0.5rem;
  color: #333;
}
</style>
