<script setup>
import { currentUser } from '@/assets/js/auth.js';
import { ref, watch, defineProps, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import PriceEvaluator from '@/components/PriceEvaluator.vue';

const showEvaluator = ref(false);
const router = useRouter();

const showWelcome = ref(false);
const displayName = ref("");

const squareFeetInput = ref('');
const rentCostInput = ref('');

defineProps({
  isDarkmode: Boolean,
});

const formattedSquareFeet = computed(() => {
  const num = parseFloat(squareFeetInput.value.replace(/,/g, ''));
  if (isNaN(num)) return '';
  return `${num.toLocaleString()} sq ft`;
})

const updateSquareFeet = (val) => {
  squareFeetInput.value = val.replace(/[^\d.]/g, '');
  squareFeet.value = parseInt(squareFeetInput.value);
}

const formattedRentCost = computed(() => {
  const num = parseFloat(rentCostInput.value.replace(/,/g, ''));
  if (isNaN(num)) return '';
  return `$${num.toLocaleString()}`;
})

const updateRentCost = (val) => {
  rentCostInput.value = val.replace(/[^\d.]/g, '');
  rentCost.value = parseFloat(rentCostInput.value);
}



onMounted(() => {
  const propertyImageInput = document.getElementById("propertyImage");
  const spinner = document.getElementById("spinner");
  const propertyForm = document.getElementById("propertyForm");

  localStorage.removeItem("predictionResult");
  localStorage.removeItem("submittedProperty");

  spinner.style.display = "none";

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



  propertyForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const address = document.getElementById("address").value;
    const bedrooms = document.getElementById("bedrooms").value;
    const bathrooms = document.getElementById("bathrooms").value;
    const squareFeet = document.getElementById("squareFeet").value;
    const rentCost = document.getElementById("rentCost").value;
    const imageFile = propertyImageInput.files[0];

    if (!address) {
      showToast("Please enter a property address to analyze!", "error");
      return;
    } else if (!bedrooms) {
      showToast("Please specify the number of bedrooms!", "error");
      return;
    } else if (!bathrooms) {
      showToast("Please specify the number of bathrooms!", "error");
      return;
    } else if (!squareFeet) {
      showToast("Please specify the size in square feet!", "error");
      return;
    } else if (!rentCost) {
      showToast("Please specify the monthly rent!", "error");
      return;
    } else if (!imageFile) {
      showToast("Please upload the file to be processed!", "error");
      return;
    }

    
      const formData = new FormData();
      formData.append("image", imageFile);
      spinner.style.display = "block";

      try {
        const response = await fetch("http://127.0.0.1:5000/check-image", {
          method: "POST",
          body: formData,
        });

        const text = await response.text();

        let data;
        try {
          data = JSON.parse(text);
          const prediction = {
            label: data.label,
            confidence: data.confidence,
          };

          const formData = {
            address,
            bedrooms,
            bathrooms,
            squareFeet,
            rentCost,
            imageFileName: imageFile ? imageFile.name : "No image uploaded",
          };

          localStorage.setItem("submittedProperty", JSON.stringify(formData));
          localStorage.setItem("predictionResult", JSON.stringify(prediction));

          if (prediction.label === "real") {
            showToast(`Your image is more than likely ${prediction.label}!`, "info");
            setTimeout(() => {
              router.push("/Dashboard");
            }, 4000);
          } else {
            showToast(`Your image is more than likely ${prediction.label}!`, "warning");
          }
        } catch (err) {
          showToast("Invalid JSON returned from server", "error");
          console.error("JSON parse error:", err);
          return;
        }
      } catch (error) {
        showToast(`Error analyzing image: ${error.message}!!`, "error");
        console.error(error);
        return;
      } finally {
        spinner.style.display = "none";
      }
  });


  watch(
    () => currentUser.value?.displayName,
    (newName) => {
      const hasWelcomed = localStorage.getItem("hasWelcomed");
      if (newName && newName !== "" && !hasWelcomed) {
        showWelcome.value = true;
        displayName.value = currentUser.value.displayName.split(" ")[0];

        localStorage.setItem("hasWelcomed", "true"); // prevent re-showing
        showToast(`Welcome back, ${displayName.value}!!`, "info");
      }
    },
    { immediate: true }
  );

});
</script>

<template>
  <div class="index-page-root">
    <section class="hero">
      <div class="hero-content">
        <div class="logo-title fade-in">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="-6 0 30 16" fill="none"
            stroke="#40a7c3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="home-icon">
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
          <h1 class="title">
            Yaad: <span class="highlight-text">Smart Property Advisor</span>
          </h1>
        </div>

        <h2 class="subtitle fade-in">Is This Property a Smart Investment?</h2>

        <p class="description fade-in">
          Get instant insights on any property. No guesswork—just smart,
          data-driven decisions.
        </p>
      </div>
      <div class="floating-icon" @click="showEvaluator = true">
        <i class="bi bi-cash-coin"></i>
      </div>

      <PriceEvaluator v-if="showEvaluator" @close="showEvaluator = false" />


      <div class="form-container slide-up">
        <form id="propertyForm" class="property-form">
          <div class="form-group">
            <label for="address">
              <div class="label-with-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="#40a7c3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
                <span>Address</span>
              </div>
            </label>
            <input type="text" id="address" placeholder="Enter property address" class="input-field" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="bedrooms">
                <div class="label-with-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="#40a7c3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2 9V4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5"></path>
                    <path d="M2 11v5a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-5"></path>
                    <path d="M2 12h20"></path>
                    <path d="M4 8h.01"></path>
                    <path d="M7 8h.01"></path>
                  </svg>
                  <span>Bedrooms</span>
                </div>
              </label>
              <input type="number" id="bedrooms" placeholder="e.g., 2" min="0" step="1" class="input-field" />
            </div>

            <div class="form-group">
              <label for="bathrooms">
                <div class="label-with-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="#40a7c3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path
                      d="M9 6 6.5 3.5a1.5 1.5 0 0 0-1-.5C4.683 3 4 3.683 4 4.5V17a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5">
                    </path>
                    <line x1="10" y1="10" x2="8" y2="12"></line>
                    <line x1="22" y1="2" x2="13" y2="11"></line>
                    <path d="M13 2v6h6"></path>
                  </svg>
                  <span>Bathrooms</span>
                </div>
              </label>
              <input type="number" id="bathrooms" placeholder="e.g., 2" min="0" step="1"  class="input-field" />
            </div>

            <div class="form-group">
              <label for="squareFeet">
                <div class="label-with-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="#40a7c3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect width="18" height="18" x="3" y="3" rx="2"></rect>
                  </svg>
                  <span>Square Feet</span>
                </div>
              </label>
              <input type="text" id="squareFeet" :value="formattedSquareFeet"
                @input="updateSquareFeet($event.target.value)" placeholder="e.g., 1,200" min="0" class="input-field" />
            </div>
          </div>

          <div class="form-group">
            <label for="rentCost">
              <div class="label-with-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="#40a7c3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 1v22"></path>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7H14a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
                <span>Monthly Rent (JMD)</span>
              </div>
            </label>
            <input type="text" id="rentCost" :value="formattedRentCost" @input="updateRentCost($event.target.value)"
              placeholder="e.g., $80,000" min="0" class="input-field" />
          </div>

          <div class="form-group">
            <label for="propertyImage">
              <div class="label-with-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="#40a7c3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="3" width="18" height="18"></rect>
                  <circle cx="8.5" cy="8.5" r="1.5"></circle>
                  <path d="M21 15l-5-5L5 21"></path>
                </svg>
                <span id="upload-image">Upload Image</span>
              </div>
            </label>
            <input type="file" id="propertyImage" accept="image/*" class="input-field" />
          </div>

          <div class="spinner-container">
            <div id="spinner" class="spinner"></div>
          </div>

          <div id="result" class="result"></div>

          <button type="submit" class="submit-button">
            <span>View Results</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
              class="chevron-icon">
              <path d="m9 18 6-6-6-6"></path>
            </svg>
          </button>
        </form>
      </div>
    </section>

    <section class="how-it-works">
      <h2 class="section-title">How It Works</h2>

      <div class="steps-container">
        <div class="step fade-in">
          <div class="step-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none"
              stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
              <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
              <path d="M12 11h4"></path>
              <path d="M12 16h4"></path>
              <path d="M8 11h.01"></path>
              <path d="M8 16h.01"></path>
            </svg>
          </div>
          <h3 class="step-title">Enter Property Details</h3>
          <p class="step-description">
            Fill in the address and basic property information to get started.
          </p>
        </div>

        <div class="step fade-in" style="animation-delay: 0.2s">
          <div class="step-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none"
              stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
          </div>
          <h3 class="step-title">AI Analyzes the Data</h3>
          <p class="step-description">
            Our algorithms evaluate the property against market data and
            investment metrics.
          </p>
        </div>

        <div class="step fade-in" style="animation-delay: 0.4s">
          <div class="step-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none"
              stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
          </div>
          <h3 class="step-title">You Get Smart Insights</h3>
          <p class="step-description">
            Receive a detailed analysis of the property's investment potential.
          </p>
        </div>
      </div>
    </section>
    <div id="toast" class="toast">
      <div class="toast-content"></div>
    </div>
  </div>
</template>

<style scoped>

.highlight-text {
  color: #40a7c3;
}

.home-icon {
  width: 40px;
  height: 40px;
  border-radius: 20%;
  box-sizing: content-box;
}

.floating-icon {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: #48b5d0;
  color: white;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  z-index: 1000;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.floating-icon:hover {
  background-color: #3aa0bb;
}
</style>
