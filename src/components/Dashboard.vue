<script setup>
import 'leaflet/dist/leaflet.css';
import { onMounted, ref } from 'vue';


const errorMsg = ref('');

const flashMessage = (prompt) => {
    setTimeout(() => {
        prompt.value = '';
  }, 2000);
}

onMounted(() => {
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

          getNearbyRestaurants(lat, lon);
        } else {
          errorMsg.value = 'Could not locate address on the map.';
          flashMessage(errorMsg);
        }
      })
      .catch(() => {
  errorMsg.value = 'Error fetching map location.'
  flashMessage(errorMsg)
})
  } else {
    errorMsg.value = 'No property data found. Submit a property first.';
    flashMessage(errorMsg);
  }

  function getNearbyRestaurants(lat, lon) {
    const radius = 1000;
    const query = `
      [out:json][timeout:25];
      (
        node["amenity"="restaurant"](around:${radius},${lat},${lon});
        way["amenity"="restaurant"](around:${radius},${lat},${lon});
        relation["amenity"="restaurant"](around:${radius},${lat},${lon});
      );
      out center;
    `;

    fetch('https://overpass-api.de/api/interpreter', {
      method: 'POST',
      body: query,
    })
      .then(res => res.json())
      .then(data => {
        const list = document.getElementById('restaurant-list');
        list.innerHTML = '';

        data.elements.forEach(element => {
          const name = element.tags?.name || 'Unnamed Restaurant';
          const latLng = element.type === 'node'
            ? [element.lat, element.lon]
            : [element.center.lat, element.center.lon];

          L.marker(latLng)
            .addTo(map)
            .bindPopup(`<strong>${name}</strong>`);

          const li = document.createElement('li');
          li.textContent = name;
          list.appendChild(li);
        });
      })
      .catch(err => {
        console.error('Error fetching restaurants:', err);
      });
  }
});
</script>

<template>

    <transition name="fade">
        <div v-if="errorMsg" class="error-message">
            {{ errorMsg }}
        </div>
    </transition>


  <div class="map-info">
      <h3>Explore the Map to View Nearby Amenities</h3>
      <p>Use the map below to discover nearby amenities, including restaurants, shops, and other services in your area.</p>
    </div>

    <div class="main-content">
      <main class="dashboard">
        <div class="container">
          <div id="map" style="height: 450px; width: 900px; border-radius: var(--radius); box-shadow: var(--shadow);"></div>
        </div>
      </main>
    </div>

    <div id="restaurant-list-container">
      <h3>Nearby Restaurants</h3>
      <ul id="restaurant-list"></ul>
    </div>

</template>

<style scoped>
.error-message {
    color: red;
    background-color: #f8d7da;
    padding: 10px;
    border-radius: 5px;
    width: 25%;
    top: 115px;
    right: 10px;
    text-align: center;
    position: absolute;
    z-index: 10;
}

.fade-leave-active {
  transition: opacity 1s ease-in-out;
}

.fade-leave-to {
  opacity: 0;
}
</style>