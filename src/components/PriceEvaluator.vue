<template>
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
          <input v-model="form['Square Footage']" type="number" id="squareFootage" class="form-control" />
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
          <input v-model="form['EstimatedRent']" type="number" id="estimatedRent" class="form-control" />
        </div>

        <div class="form-group form-grid">
          <label v-for="feature in binaryFeatures" :key="feature" class="form-checkbox-label">
            <input
              v-model="form[feature]"
              type="checkbox"
              :true-value="1"
              :false-value="0"
              :id="feature"
              class="form-checkbox-input"
            />
            <span>{{ formatLabel(feature) }}</span>
          </label>
        </div>
      </div>

      <div class="popup-footer">
        <button @click="evaluate" class="popup-button">Evaluate</button>

        <div v-if="result" class="popup-result">
          <p class="result-predicted-value">
            Predicted Monthly Rent: ${{ result.predicted_value.toLocaleString() }}
          </p>
          <p class="result-verdict">
            {{ verdictText }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const result = ref(null)
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




const evaluate = async () => {
  const response = await fetch('http://localhost:5000/api/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value),
  })
  const data = await response.json()

  if (data.predicted_value !== undefined) {
    result.value = data
  } else {
    result.value = null
  }
}
</script>

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
}

.popup-button {
  background-color: #4caf50;
  color: white;
  padding: 0.9rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
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
