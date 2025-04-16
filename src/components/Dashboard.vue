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
          getNearbySchools(lat, lon);
          getNearbyPlacesOfWorship(lat, lon);
          getNearbyHospitals(lat, lon);
          getNearbyFastFood(lat, lon);
          getNearbyBanks(lat, lon);
          getNearbyPharmacies(lat,lon);
          getNearbyPoliceStations(lat,lon);
          getNearbyDoctors(lat, lon);
          getNearbySupermarkets(lat, lon);
          getNearbyFitnessCentres(lat, lon);
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
      const list = document.getElementById('restaurants-list');
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



  function getNearbySchools(lat, lon) {
    const radius = 1000;
    const query = `
      [out:json][timeout:25];
      (
        node["amenity"="school"](around:${radius},${lat},${lon});
        way["amenity"="school"](around:${radius},${lat},${lon});
        relation["amenity"="school"](around:${radius},${lat},${lon});
      );
      out center;
    `;

    fetch('https://overpass-api.de/api/interpreter', {
      method: 'POST',
      body: query,
    })
      .then(res => res.json())
      .then(data => {
        const list = document.getElementById('school-list');
        list.innerHTML = '';

        data.elements.forEach(element => {
          const name = element.tags?.name || 'Unnamed School';
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
        console.error('Error fetching school:', err);
      });
  }

  function getNearbyPlacesOfWorship(lat, lon) {
  const radius = 1000;
  const query = `
    [out:json][timeout:25];
    (
      node["amenity"="place_of_worship"](around:${radius},${lat},${lon});
      way["amenity"="place_of_worship"](around:${radius},${lat},${lon});
      relation["amenity"="place_of_worship"](around:${radius},${lat},${lon});
    );
    out center;
  `;

  fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: query,
  })
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('place-of-worship-list');
      list.innerHTML = '';

      data.elements.forEach(element => {
        const name = element.tags?.name || 'Unnamed Place of Worship';
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
      console.error('Error fetching places of worship:', err);
    });
}

function getNearbyHospitals(lat, lon) {
  const radius = 1000;
  const query = `
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:${radius},${lat},${lon});
      way["amenity"="hospital"](around:${radius},${lat},${lon});
      relation["amenity"="hospital"](around:${radius},${lat},${lon});
    );
    out center;
  `;

  fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: query,
  })
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('hospital-list');
      list.innerHTML = '';

      data.elements.forEach(element => {
        const name = element.tags?.name || 'Unnamed Hospital';
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
      console.error('Error fetching hospitals:', err);
    });
}

function getNearbyFastFood(lat, lon) {
  const radius = 1000;
  const query = `
    [out:json][timeout:25];
    (
      node["amenity"="fast_food"](around:${radius},${lat},${lon});
      way["amenity"="fast_food"](around:${radius},${lat},${lon});
      relation["amenity"="fast_food"](around:${radius},${lat},${lon});
    );
    out center;
  `;

  fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: query,
  })
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('fast-food-list');
      list.innerHTML = '';

      data.elements.forEach(element => {
        const name = element.tags?.name || 'Unnamed Fast Food Place';
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
      console.error('Error fetching fast food places:', err);
    });
}

function getNearbyBanks(lat, lon) {
  const radius = 1000;
  const query = `
    [out:json][timeout:25];
    (
      node["amenity"="bank"](around:${radius},${lat},${lon});
      way["amenity"="bank"](around:${radius},${lat},${lon});
      relation["amenity"="bank"](around:${radius},${lat},${lon});
    );
    out center;
  `;

  fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: query,
  })
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('bank-list');
      list.innerHTML = '';

      data.elements.forEach(element => {
        const name = element.tags?.name || 'Unnamed Bank';
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
      console.error('Error fetching banks:', err);
    });
}

function getNearbyPharmacies(lat, lon) {
  const radius = 1000;
  const query = `
    [out:json][timeout:25];
    (
      node["amenity"="pharmacy"](around:${radius},${lat},${lon});
      way["amenity"="pharmacy"](around:${radius},${lat},${lon});
      relation["amenity"="pharmacy"](around:${radius},${lat},${lon});
    );
    out center;
  `;

  fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: query,
  })
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('pharmacy-list');
      list.innerHTML = '';

      data.elements.forEach(element => {
        const name = element.tags?.name || 'Unnamed Pharmacy';
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
      console.error('Error fetching pharmacies:', err);
    });
}

function getNearbyPoliceStations(lat, lon) {
  const radius = 1000;
  const query = `
    [out:json][timeout:25];
    (
      node["amenity"="police"](around:${radius},${lat},${lon});
      way["amenity"="police"](around:${radius},${lat},${lon});
      relation["amenity"="police"](around:${radius},${lat},${lon});
    );
    out center;
  `;

  fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: query,
  })
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('police-list');
      list.innerHTML = '';

      data.elements.forEach(element => {
        const name = element.tags?.name || 'Unnamed Police Station';
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
      console.error('Error fetching police stations:', err);
    });
}

function getNearbyDoctors(lat, lon) {
  const radius = 1000;
  const query = `
    [out:json][timeout:25];
    (
      node["amenity"="doctors"](around:${radius},${lat},${lon});
      way["amenity"="doctors"](around:${radius},${lat},${lon});
      relation["amenity"="doctors"](around:${radius},${lat},${lon});
    );
    out center;
  `;

  fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: query,
  })
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('doctors-list');
      list.innerHTML = '';

      data.elements.forEach(element => {
        const name = element.tags?.name || 'Unnamed Doctor\'s Office';
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
      console.error('Error fetching doctors:', err);
    });
}

function getNearbySupermarkets(lat, lon) {
  const radius = 1000;
  const query = `
    [out:json][timeout:25];
    (
      node["shop"="supermarket"](around:${radius},${lat},${lon});
      way["shop"="supermarket"](around:${radius},${lat},${lon});
      relation["shop"="supermarket"](around:${radius},${lat},${lon});
    );
    out center;
  `;

  fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: query,
  })
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('supermarket-list');
      list.innerHTML = '';

      data.elements.forEach(element => {
        const name = element.tags?.name || 'Unnamed Supermarket';
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
      console.error('Error fetching supermarkets:', err);
    });
}

function getNearbyFitnessCentres(lat, lon) {
  const radius = 1000;
  const query = `
    [out:json][timeout:25];
    (
      node["leisure"="fitness_centre"](around:${radius},${lat},${lon});
      way["leisure"="fitness_centre"](around:${radius},${lat},${lon});
      relation["leisure"="fitness_centre"](around:${radius},${lat},${lon});
    );
    out center;
  `;

  fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: query,
  })
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('fitness-centre-list');
      list.innerHTML = '';

      data.elements.forEach(element => {
        const name = element.tags?.name || 'Unnamed Fitness Centre';
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
      console.error('Error fetching fitness centres:', err);
    });
}

});
</script>




<template>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">


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

</style>