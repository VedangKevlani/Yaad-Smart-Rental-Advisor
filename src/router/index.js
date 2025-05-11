import { createRouter, createWebHistory } from 'vue-router'
import HomePage from 'src/components/HomePage.vue'
import IndexPage from 'src/components/IndexPage.vue'
import SignUp from 'src/components/SignUp.vue'
import Login from 'src/components/Login.vue'
import SignOut from 'src/components/SignOut.vue'
import Dashboard from 'src/components/Dashboard.vue'
import InvestmentTools from 'src/components/InvestmentTools.vue'
import MyProfile from '../components/MyProfile.vue'

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
    },
    {
      path: '/my-profile',
      name: 'myprofile',
      component: MyProfile
    }
  ]
})

export default router
