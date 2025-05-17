import { createApp } from 'vue'
import App from 'src/App.vue'
import router from 'src/router/index.js'
import 'src/assets/css/style.css'
import 'src/assets/js/auth.js';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'src/assets/js/investments.js'

const app = createApp(App)

app.use(router)

app.mount('#app')
