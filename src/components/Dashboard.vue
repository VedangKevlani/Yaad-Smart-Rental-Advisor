<script setup>
import 'leaflet/dist/leaflet.css';
import { onMounted, ref } from 'vue';
import PriceEvaluator from '@/components/PriceEvaluator.vue';

const showEvaluator = ref(false);
const errorMsg = ref('');
const showPopup = ref(false);


const predictionLabel = ref("");
const predictionConfidence = ref("");

function showToast(message, type) {
  const toast = document.querySelector("#toast");
  const toastContent = toast.querySelector(".toast-content");

  if (!toast || !toastContent) {
    console.error("Toast element or content not found.");
    return;
  }

  toastContent.textContent = message;
  toast.classList.add("show", type);

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

onMounted(() => {
  const stored = localStorage.getItem("predictionResult");
  if (stored) {
    const result = JSON.parse(stored);
    predictionLabel.value = result.label;
    predictionConfidence.value = result.confidence;
    showToast(`Prediction: Your image is most likely ${predictionLabel.value}!`, "info");
  }

  const storedData = localStorage.getItem('submittedProperty');


  let map = L.map('map').setView([18.0155, -76.8766], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors',
  }).addTo(map);

  let currentMarker;

  if (storedData) {
    const { address } = JSON.parse(storedData);

    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`)
      .then(res => res.json())
      .then(data => {
        if (data && data.length > 0) {
          const lat = parseFloat(data[0].lat);
          const lon = parseFloat(data[0].lon);

          map.setView([lat, lon], 15);

          currentMarker = L.marker([lat, lon])
            .addTo(map)
            .bindPopup(`<strong>${address}</strong>`)
            .openPopup();

          getAmenities(lat, lon);
        } else {
          errorMsg.value = 'Could not locate address on the map.';
          showToast(errorMsg.value, 'error');
        }
      })
      .catch(() => {
        errorMsg.value = 'Error fetching map location.';
        showToast(errorMsg.value, 'error');
      });
  } else {
    errorMsg.value = 'No property data found. Submit a property first.';
    showToast(errorMsg.value, 'error');
  }

  function getAmenities(lat, lon) {
    const amenityTypes = [
      { key: 'restaurant', listId: 'restaurants-list', label: 'Unnamed Restaurant' },
      { key: 'school', listId: 'school-list', label: 'Unnamed School' },
      { key: 'place_of_worship', listId: 'place-of-worship-list', label: 'Unnamed Place of Worship' },
      { key: 'hospital', listId: 'hospital-list', label: 'Unnamed Hospital' },
      { key: 'fast_food', listId: 'fast-food-list', label: 'Unnamed Fast Food Place' },
      { key: 'bank', listId: 'bank-list', label: 'Unnamed Bank' },
      { key: 'pharmacy', listId: 'pharmacy-list', label: 'Unnamed Pharmacy' },
      { key: 'police', listId: 'police-list', label: 'Unnamed Police Station' },
      { key: 'doctors', listId: 'doctors-list', label: "Unnamed Doctor's Office" },
      { key: 'supermarket', listId: 'supermarket-list', label: 'Unnamed Supermarket', isShop: true },
      { key: 'fitness_centre', listId: 'fitness-list', label: 'Unnamed Fitness Centre' },
    ];

    amenityTypes.forEach(({ key, listId, label, isShop }) => {
      const radius = 1000;
      const query = `
        [out:json][timeout:25];
        (
          node["${isShop ? 'shop' : 'amenity'}"="${key}"](around:${radius},${lat},${lon});
          way["${isShop ? 'shop' : 'amenity'}"="${key}"](around:${radius},${lat},${lon});
          relation["${isShop ? 'shop' : 'amenity'}"="${key}"](around:${radius},${lat},${lon});
        );
        out center;
      `;

      fetch('https://overpass-api.de/api/interpreter', {
        method: 'POST',
        body: query,
      })
        .then(res => res.json())
        .then(data => {
          const list = document.getElementById(listId);
          list.innerHTML = '';

          data.elements.forEach(element => {
            const name = element.tags?.name || label;

            if (name.toLowerCase().startsWith('unnamed')) return;

            const latLng = element.type === 'node'
              ? [element.lat, element.lon]
              : [element.center.lat, element.center.lon];

            L.marker(latLng)
              .addTo(map)
              .bindPopup(`<strong>${name}</strong>`);

            const li = document.createElement('li');
            li.textContent = name;
            list.appendChild(li);

            const spacer = document.createElement('br');
            list.appendChild(spacer);
          });
        })
        .catch(err => {
          console.error(`Error fetching ${key}:`, err);
        });
    });
  }
});
</script>



<template>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">


  <div id="toast" class="toast">
    <div class="toast-content"></div>
  </div>

  <div class="map-info">
    <h3>Explore the Map to View Nearby Amenities</h3>
    <p>Use the map below to discover nearby amenities, including restaurants, shops, and other services in your area.
    </p>
  </div>

  <div class="main-content">
    <main class="dashboard">
      <div class="container">
        <div id="map" style="height: 450px; width: 900px; border-radius: var(--radius); box-shadow: var(--shadow);">
        </div>
      </div>
    </main>
  </div>


  <div id="amenitiesCarousel" class="carousel slide">

    <div class="carousel-inner">


      <div class="carousel-item active">
        <div class="d-flex justify-content-center flex-wrap gap-3">
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title"><i class="bi bi-house-door me-2"></i> Restaurants</h5>
              <ul id="restaurants-list" class="list-unstyled mb-0"></ul>
            </div>
          </div>
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title"><i class="bi bi-building me-2"></i> Schools</h5>
              <ul id="school-list" class="list-unstyled mb-0"></ul>
            </div>
          </div>
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title"><i class="bi bi-buildings"></i> Places of Worship</h5>
              <ul id="place-of-worship-list" class="list-unstyled mb-0"></ul>
            </div>
          </div>
        </div>
      </div>

      <div class="carousel-item">
        <div class="d-flex justify-content-center flex-wrap gap-3">
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title"><i class="bi bi-hospital me-2"></i> Hospitals</h5>
              <ul id="hospital-list" class="list-unstyled mb-0"></ul>
            </div>
          </div>
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title"><i class="bi bi-cup-straw me-2"></i> Fast Food</h5>
              <ul id="fast-food-list" class="list-unstyled mb-0"></ul>
            </div>
          </div>
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title"><i class="bi bi-bank me-2"></i> Banks</h5>
              <ul id="bank-list" class="list-unstyled mb-0"></ul>
            </div>
          </div>
        </div>
      </div>

      <div class="carousel-item">
        <div class="d-flex justify-content-center flex-wrap gap-3">
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title"><i class="bi bi-capsule-pill"></i> Pharmacies</h5>
              <ul id="pharmacy-list" class="list-unstyled mb-0"></ul>
            </div>
          </div>
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title"><i class="bi bi-shield-lock me-2"></i> Police Stations</h5>
              <ul id="police-list" class="list-unstyled mb-0"></ul>
            </div>
          </div>
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title"><i class="bi bi-person-circle me-2"></i> Doctors</h5>
              <ul id="doctors-list" class="list-unstyled mb-0"></ul>
            </div>
          </div>
        </div>
      </div>

      <div class="carousel-item">
        <div class="d-flex justify-content-center flex-wrap gap-3">
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title"><i class="bi bi-shop me-2"></i> Supermarkets</h5>
              <ul id="supermarket-list" class="list-unstyled mb-0"></ul>
            </div>
          </div>
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <h5 class="card-title"><i class="bi bi-activity me-2"></i> Fitness Centres</h5>
              <ul id="fitness-centre-list" class="list-unstyled mb-0"></ul>
            </div>
          </div>
        </div>
      </div>

    </div>

    <button class="carousel-control-prev" type="button" data-bs-target="#amenitiesCarousel" data-bs-slide="prev">
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Previous</span>
    </button>

    <button class="carousel-control-next" type="button" data-bs-target="#amenitiesCarousel" data-bs-slide="next">
      <span class="carousel-control-next-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Next</span>
    </button>
  </div>

  <div class="floating-icon" @click="showEvaluator = true">
    <i class="bi bi-cash-coin"></i>
  </div>

  <PriceEvaluator v-if="showEvaluator" @close="showEvaluator = false" />


  <transition name="fade">
    <div v-if="showPopup" class="popup-overlay" @click.self="showPopup = false">
      <div class="popup-content">
        <h5 class="mb-3">Price Evaluator</h5>
        <p>Enter price details here...</p>
        <button class="btn btn-secondary btn-sm mt-2" @click="showPopup = false">Close</button>
      </div>
    </div>
  </transition>

</template>

<style scoped>
.toast {
  position: fixed;
  top: 120px;
  right: 30px;
  background: #333;
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 9999;
  max-height: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.toast.show {
  opacity: 1;
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

.nav-button {
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

.nav-button:hover {
  background-color: black;
  color: #fff;
  border-color: black;
}

.card {
  border: 1px solid #ddd;
  border-radius: 8px;
}

.card-body {
  padding: 1.25rem;
  align-items: center;
}

.card-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.card ul {
  padding: 0;
  list-style: none;
}

.container {
  padding-top: 2rem;
  padding-bottom: 2rem;
}

.card-body ul {
  margin-top: 0;
  margin-bottom: 0;
}

.card-body ul li {
  margin-bottom: 1rem;
}

.carousel-control-prev-icon,
.carousel-control-next-icon {
  background-color: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  padding: 1rem;
}

.carousel-inner {
  display: flex;
  align-items: center;
  transition: height 0.5s ease;
  min-height: 300px;
  padding-bottom: 5%;
}

.popup-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.popup-content {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  width: 300px;
  max-width: 90%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  animation: pop 0.3s ease-in-out;
}

@keyframes pop {
  from {
    transform: scale(0.9);
    opacity: 0;
  }

  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>