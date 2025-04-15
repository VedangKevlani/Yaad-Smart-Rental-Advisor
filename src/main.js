import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import '../src/style.css'
import './auth.js';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './investments.js'

const app = createApp(App)

app.use(router)

app.mount('#app')
