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
        alert('Could not locate address on the map.');
      }
    })
    .catch(() => alert('Error fetching map location.'));
} else {
  alert('No property data found. Submit a property first.');
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
  