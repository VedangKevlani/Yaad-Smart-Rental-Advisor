<script setup>
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { onMounted, onBeforeUnmount, ref } from 'vue';
import PriceEvaluator from '@/components/PriceEvaluator.vue';

const showEvaluator = ref(false);
const errorMsg = ref('');
const showPopup = ref(false);

// Same-origin /api (Vercel function) unless an external API is configured.
const API_BASE = import.meta.env.VITE_API_URL || '';
const SEARCH_RADIUS_M = 1500;

// One entry per list on the page. Colours/icons are drawn with CSS (divIcon),
// so every category gets its own marker and the legend always matches.
const CATEGORIES = [
  { key: 'restaurant', listId: 'restaurants-list', label: 'Restaurant', color: '#8e44ad', icon: 'bi-cup-hot' },
  { key: 'fast_food', listId: 'fast-food-list', label: 'Fast Food', color: '#e67e22', icon: 'bi-cup-straw' },
  { key: 'school', listId: 'school-list', label: 'School', color: '#d4ac0d', icon: 'bi-mortarboard' },
  { key: 'place_of_worship', listId: 'place-of-worship-list', label: 'Place of Worship', color: '#6d4c41', icon: 'bi-buildings' },
  { key: 'hospital', listId: 'hospital-list', label: 'Hospital', color: '#c0392b', icon: 'bi-hospital' },
  { key: 'doctors', listId: 'doctors-list', label: 'Doctor / Clinic', color: '#e84393', icon: 'bi-heart-pulse' },
  { key: 'pharmacy', listId: 'pharmacy-list', label: 'Pharmacy', color: '#27ae60', icon: 'bi-capsule-pill' },
  { key: 'bank', listId: 'bank-list', label: 'Bank / ATM', color: '#2c3e50', icon: 'bi-bank' },
  { key: 'police', listId: 'police-list', label: 'Police Station', color: '#2058c9', icon: 'bi-shield-lock' },
  { key: 'supermarket', listId: 'supermarket-list', label: 'Supermarket', color: '#b7950b', icon: 'bi-cart' },
  { key: 'mall', listId: 'mall-list', label: 'Mall', color: '#16a085', icon: 'bi-bag' },
  { key: 'fitness_centre', listId: 'fitness-centre-list', label: 'Fitness Centre', color: '#7f8c8d', icon: 'bi-activity' },
];
const BY_KEY = Object.fromEntries(CATEGORIES.map((c) => [c.key, c]));

function pinIcon(color, icon, size = 30) {
  return L.divIcon({
    className: 'poi-pin-wrap',
    html: `<div class="poi-pin" style="background:${color};width:${size}px;height:${size}px"><i class="bi ${icon}"></i></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size],
    popupAnchor: [0, -size],
  });
}
const homeIcon = pinIcon('#e53935', 'bi-house-door-fill', 38);

const HTML_ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => HTML_ESCAPES[c]);
}

function distanceM(a, b) {
  const R = 6371000, rad = Math.PI / 180;
  const dLat = (b[0] - a[0]) * rad, dLon = (b[1] - a[1]) * rad;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(a[0] * rad) * Math.cos(b[0] * rad) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

function showToast(message, type) {
  const toast = document.querySelector('#toast');
  const toastContent = toast?.querySelector('.toast-content');
  if (!toast || !toastContent) {
    console.error('Toast element or content not found.');
    return;
  }
  toast.classList.remove('show', type);
  toastContent.textContent = message;
  toast.classList.add('show', type);
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

function setAllLists(html) {
  CATEGORIES.forEach(({ listId }) => {
    const list = document.getElementById(listId);
    if (list) list.innerHTML = html;
  });
}

async function getJson(url, tries = 2) {
  let lastErr;
  for (let i = 0; i < tries; i++) {
    try {
      const res = await fetch(url);
      const data = await res.json().catch(() => ({}));
      if (res.ok) return data;
      lastErr = new Error(data.error || `HTTP ${res.status}`);
      if (res.status < 500) break;
    } catch (e) {
      lastErr = e;
    }
    await new Promise((r) => setTimeout(r, 1000));
  }
  throw lastErr;
}

let map;

onMounted(async () => {
  const mapElement = document.getElementById('map');
  const storedData = localStorage.getItem('submittedProperty');

  map = L.map('map').setView([18.0155, -76.8766], 13);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors',
  }).addTo(map);

  const legend = L.control({ position: 'bottomright' });
  legend.onAdd = function () {
    const div = L.DomUtil.create('div', 'info legend map-legend');
    div.innerHTML = '<h4>Amenities</h4>' +
      [{ label: 'Your property', color: '#e53935' }, ...CATEGORIES]
        .map(({ label, color }) => `<div class="legend-row"><span style="background:${color}"></span>${escapeHtml(label)}</div>`)
        .join('');
    return div;
  };
  legend.addTo(map);

  if (!storedData) {
    errorMsg.value = 'No property data found. Submit a property first.';
    showToast(errorMsg.value, 'error');
    return;
  }
  setAllLists('<p class="text-muted small mb-0">Loading…</p>');

  const { address } = JSON.parse(storedData);
  let home;
  try {
    const g = await getJson(`${API_BASE}/api/geocode?q=${encodeURIComponent(address)}`);
    home = [g.lat, g.lon];
  } catch (e) {
    errorMsg.value = /not found/i.test(e.message) ? 'Could not locate address on the map.' : 'Error fetching map location.';
    showToast(errorMsg.value, 'error');
    setAllLists('');
    return;
  }

  map.setView(home, 15);
  L.marker(home, { icon: homeIcon, zIndexOffset: 1000 })
    .addTo(map)
    .bindPopup(`<strong>${escapeHtml(address)}</strong>`)
    .openPopup();
  L.circle(home, { radius: SEARCH_RADIUS_M, color: '#40a7c3', weight: 1, fillOpacity: 0.04 }).addTo(map);

  let places;
  try {
    ({ places } = await getJson(`${API_BASE}/api/amenities?lat=${home[0]}&lon=${home[1]}&radius=${SEARCH_RADIUS_M}`, 3));
  } catch (e) {
    console.error('Error fetching amenities:', e);
    showToast('Could not load nearby amenities. Please try again shortly.', 'error');
    setAllLists('<p class="text-muted small mb-0">Unavailable right now.</p>');
    return;
  }

  const lists = Object.fromEntries(CATEGORIES.map((c) => [c.key, []]));
  for (const p of places) {
    const cat = BY_KEY[p.category];
    if (!cat) continue;
    const latLng = [p.lat, p.lon];
    const title = p.name || cat.label;
    const marker = L.marker(latLng, { icon: pinIcon(cat.color, cat.icon) })
      .addTo(map)
      .bindPopup(`<strong>${escapeHtml(title)}</strong><br><small>${escapeHtml(cat.label)}</small>`);
    if (p.name) lists[cat.key].push({ name: p.name, latLng, marker, dist: distanceM(home, latLng) });
  }

  CATEGORIES.forEach(({ key, listId }) => {
    const list = document.getElementById(listId);
    if (!list) return;
    list.innerHTML = '';
    const items = lists[key].sort((a, b) => a.dist - b.dist);
    if (!items.length) {
      list.innerHTML = '<p class="text-muted small mb-0">None found nearby.</p>';
      return;
    }
    items.forEach(({ name, latLng, marker, dist }) => {
      const link = document.createElement('p');
      link.textContent = `${name} (${dist < 1000 ? Math.round(dist) + ' m' : (dist / 1000).toFixed(1) + ' km'})`;
      link.style.cursor = 'pointer';
      link.className = 'link';
      link.addEventListener('click', (e) => {
        e.preventDefault();
        mapElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        map.setView(latLng, 18);
        setTimeout(() => marker.openPopup(), 200);
      });
      list.appendChild(link);
    });
  });
});

onBeforeUnmount(() => {
  if (map) map.remove();
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
                <h5 class="card-title"><i class="bi bi-person-circle me-2"></i> Doctors &amp; Clinics</h5>
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
                <h5 class="card-title"><i class="bi bi-bag me-2"></i> Malls</h5>
                <div id="mall-list" class="list-unstyled mb-0"></div>
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

<style>
/* Leaflet builds marker/legend DOM itself, so these styles cannot be scoped. */
.poi-pin-wrap { background: none; border: none; }
.poi-pin {
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.45);
}
.poi-pin i { transform: rotate(45deg); color: #fff; font-size: 14px; line-height: 1; }
.map-legend {
  background: rgba(255, 255, 255, 0.92);
  padding: 6px 9px;
  border-radius: 6px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.3);
  color: #000;
  font-size: 11px;
  line-height: 1.2;
}
.map-legend h4 { font-size: 13px; font-weight: bold; text-decoration: underline; margin: 0 0 4px; color: #000; }
.map-legend .legend-row { display: flex; align-items: center; margin-bottom: 2px; font-weight: bold; }
.map-legend .legend-row span {
  width: 12px; height: 12px; border-radius: 50%; margin-right: 7px; border: 1px solid #fff;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.4); display: inline-block;
}
</style>
