<script setup>
import 'leaflet/dist/leaflet.css';
import { onMounted, ref } from 'vue';
import PriceEvaluator from '@/components/PriceEvaluator.vue';

const showEvaluator = ref(false);
const errorMsg = ref('');
const showPopup = ref(false);


const redIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const colorIcons = {
  violet: new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-violet.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  }),
  yellow: new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-yellow.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  }),
  grey: new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-grey.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  }),
  orange: new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  }),
  black: new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-black.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  }),
  green: new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  }),
  blue: new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  }),
  gold: new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-gold.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  }),
}


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
    toast.classList.remove("show");
  }, 3000);
}

onMounted(() => {
  const mapElement = document.getElementById('map');
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

          currentMarker = L.marker([lat, lon], { icon: redIcon })
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
      { key: 'restaurant', listId: 'restaurants-list', label: 'Unnamed Restaurant', color: 'violet' },
      { key: 'school', listId: 'school-list', label: 'Unnamed School', color: 'yellow' },
      { key: 'place_of_worship', listId: 'place-of-worship-list', label: 'Unnamed Place of Worship', color: '' },
      { key: 'hospital', listId: 'hospital-list', label: 'Unnamed Hospital', color: 'grey' },
      { key: 'fast_food', listId: 'fast-food-list', label: 'Unnamed Fast Food Place', color: 'orange' },
      { key: 'bank', listId: 'bank-list', label: 'Unnamed Bank', color: 'black' },
      { key: 'pharmacy', listId: 'pharmacy-list', label: 'Unnamed Pharmacy', color: 'green' },
      { key: 'police', listId: 'police-list', label: 'Unnamed Police Station', color: 'blue' },
      { key: 'doctors', listId: 'doctors-list', label: "Unnamed Doctor's Office", color: '' },
      { key: 'supermarket', listId: 'supermarket-list', label: 'Unnamed Supermarket', isShop: true, color: 'gold' },
      { key: 'fitness_centre', listId: 'fitness-centre-list', label: 'Unnamed Fitness Centre', color: '' },
    ];

    amenityTypes.forEach(({ key, listId, label, isShop, color }) => {
      const radius = 1000;
      const query = `
        [out:json][timeout:45];
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
          if (!list) {
            console.error(`Element with id "${listId}" not found in the DOM.`);
            return;
          }
          list.innerHTML = '';

          data.elements.forEach(element => {
            const name = element.tags?.name || label;
            const markerColor = element.tags?.colour || color;
            const icon = colorIcons[markerColor] || colorIcons.grey;

            if (name.toLowerCase().startsWith('unnamed')) return;

            const latLng = element.type === 'node'
              ? [element.lat, element.lon]
              : [element.center.lat, element.center.lon];

            const marker = L.marker(latLng, { icon })
              .addTo(map)
              .bindPopup(`<strong>${name}</strong>`);

            const link = document.createElement('p');
            link.textContent = name;
            link.style.cursor = 'pointer';
            link.className = "link";

            link.addEventListener('mouseenter', () => {
              if (document.body.classList.contains('dark-mode')) {
                link.classList.add("dark-mode");
              } else {
                link.classList.remove("dark-mode");
              }
            });

            link.addEventListener('mouseleave', () => {
              if (document.body.classList.contains('dark-mode')) {
                link.classList.add("dark-mode");
              } else {
                link.classList.remove("dark-mode");
              }
            });


            link.addEventListener('click', (e) => {
              e.preventDefault();
              mapElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
              map.setView(latLng, 18);
              setTimeout(() => marker.openPopup(), 200);
            });
            list.appendChild(link);


          });
        })
        .catch(err => {
          console.error(`Error fetching ${key}:`, err);
        });
    });
  }

  const legend = L.control({ position: 'bottomright' });

  legend.onAdd = function (map) {
    const div = L.DomUtil.create('div', 'info legend');
    const amenities = [
      { label: 'Bank', color: 'black' },
      { label: 'Fast Food', color: 'orange' },
      { label: 'Pharmacy', color: 'green' },
      { label: 'Police Station', color: 'blue' },
      { label: 'Restaurant', color: 'violet' },
      { label: 'School', color: 'yellow' },
      { label: 'Supermarket', color: 'gold' },
      { label: 'Other', color: 'grey' }
    ];

    div.innerHTML += '<h4 style="color: black; font-weight: bold; text-decoration: underline;">Amenities</h4>';
    amenities.forEach(({ label, color }) => {
      div.innerHTML += `
      <div style="display: flex; align-items: center; margin-bottom: 4px; color: black; font-weight:bold;">
        <span style="
          background-color: ${color};
          width: 16px;
          height: 16px;
          display: inline-block;
          margin-right: 8px;
          border: 1px solid #000;
        "></span> ${label}
      </div>`;
    });

    return div;
  };

  legend.addTo(map);

});
</script>



<template>
  <div class="dashboard-root">
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
                <div id="restaurants-list" class="list-unstyled mb-0"></div>
              </div>
            </div>
            <div class="card" style="width: 18rem;">
              <div class="card-body">
                <h5 class="card-title"><i class="bi bi-building me-2"></i> Schools</h5>
                <div id="school-list" class="list-unstyled mb-0"></div>
              </div>
            </div>
            <div class="card" style="width: 18rem;">
              <div class="card-body">
                <h5 class="card-title"><i class="bi bi-buildings"></i> Places of Worship</h5>
                <div id="place-of-worship-list" class="list-unstyled mb-0"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="carousel-item">
          <div class="d-flex justify-content-center flex-wrap gap-3">
            <div class="card" style="width: 18rem;">
              <div class="card-body">
                <h5 class="card-title"><i class="bi bi-hospital me-2"></i> Hospitals</h5>
                <div id="hospital-list" class="list-unstyled mb-0"></div>
              </div>
            </div>
            <div class="card" style="width: 18rem;">
              <div class="card-body">
                <h5 class="card-title"><i class="bi bi-cup-straw me-2"></i> Fast Food</h5>
                <div id="fast-food-list" class="list-unstyled mb-0"></div>
              </div>
            </div>
            <div class="card" style="width: 18rem;">
              <div class="card-body">
                <h5 class="card-title"><i class="bi bi-bank me-2"></i> Banks</h5>
                <div id="bank-list" class="list-unstyled mb-0"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="carousel-item">
          <div class="d-flex justify-content-center flex-wrap gap-3">
            <div class="card" style="width: 18rem;">
              <div class="card-body">
                <h5 class="card-title"><i class="bi bi-capsule-pill"></i> Pharmacies</h5>
                <div id="pharmacy-list" class="list-unstyled mb-0"></div>
              </div>
            </div>
            <div class="card" style="width: 18rem;">
              <div class="card-body">
                <h5 class="card-title"><i class="bi bi-shield-lock me-2"></i> Police Stations</h5>
                <div id="police-list" class="list-unstyled mb-0"></div>
              </div>
            </div>
            <div class="card" style="width: 18rem;">
              <div class="card-body">
                <h5 class="card-title"><i class="bi bi-person-circle me-2"></i> Doctors</h5>
                <div id="doctors-list" class="list-unstyled mb-0"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="carousel-item">
          <div class="d-flex justify-content-center flex-wrap gap-3">
            <div class="card" style="width: 18rem;">
              <div class="card-body">
                <h5 class="card-title"><i class="bi bi-shop me-2"></i> Supermarkets</h5>
                <div id="supermarket-list" class="list-unstyled mb-0"></div>
              </div>
            </div>
            <div class="card" style="width: 18rem;">
              <div class="card-body">
                <h5 class="card-title"><i class="bi bi-activity me-2"></i> Fitness Centres</h5>
                <div id="fitness-centre-list" class="list-unstyled mb-0"></div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <button class="custom-carousel-btn carousel-control-prev" type="button" data-bs-target="#amenitiesCarousel"
        data-bs-slide="prev">
        <span class="custom-arrow">&#10094;</span>
        <span class="visually-hidden">Previous</span>
      </button>

      <button class="custom-carousel-btn carousel-control-next" type="button" data-bs-target="#amenitiesCarousel"
        data-bs-slide="next">
        <span class="custom-arrow">&#10095;</span>
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
  </div>
</template>

<style scoped>
.custom-div-icon {
  text-align: center;
}

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

div[id$="list"] * {
  color: black;
}

div[id$="list"] *:hover {
  color: blue;
}

.dark-mode div[id$="list"] * {
  color: white;
}

.dark-mode div[id$="list"] *:hover {
  color: gold;
}

.dark-mode .card-body {
  background-color: #0f172a;
  color: white;
}

.dark-mode .card {
  border: 1px solid #0c1431;
}

.carousel {
  margin-bottom: 30px;
}

.custom-carousel-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
  border: none;
  position: absolute;
  top: 30%;
  transform: translateY(-50%);
  z-index: 1;
}

.carousel-control-prev.custom-carousel-btn {
  left: 120px;
}

.carousel-control-next.custom-carousel-btn {
  right: 120px;
}

.custom-carousel-btn:hover {
  background-color: rgba(0, 0, 0, 0.8);
}

.custom-arrow {
  color: #fff;
  font-size: 24px;
  line-height: 1;
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