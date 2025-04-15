import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../components/HomePage.vue'
import IndexPage from '../components/IndexPage.vue'
import SignUp from '../components/SignUp.vue'
import Login from '../components/Login.vue'
import SignOut from '../components/SignOut.vue'
import Dashboard from '../components/Dashboard.vue'
import InvestmentTools from '../components/InvestmentTools.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage
    },
    {
      path: '/index',
      name: 'index',
      component: IndexPage
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUp
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/signout',
      name: 'signout',
      component: SignOut
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/investment-tools',
      name: 'investmenttools',
      component: InvestmentTools
    }
  ]
})

export default router
