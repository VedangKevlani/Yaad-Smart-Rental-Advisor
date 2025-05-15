import { createRouter, createWebHistory } from 'vue-router'
import HomePage from 'src/components/HomePage.vue'
import IndexPage from 'src/components/IndexPage.vue'
import SignUp from 'src/components/SignUp.vue'
import Login from 'src/components/Login.vue'
import SignOut from 'src/components/SignOut.vue'
import Dashboard from 'src/components/Dashboard.vue'
import InvestmentTools from 'src/components/InvestmentTools.vue'
import MyProfile from 'src/components/MyProfile.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: { transition: 'custom' }
    },
    {
      path: '/index',
      name: 'index',
      component: IndexPage,
      meta: { transition: 'custom' }
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUp,
      meta: { transition: 'custom' }
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { transition: 'custom' }
    },
    {
      path: '/signout',
      name: 'signout',
      component: SignOut,
      meta: { transition: 'custom' }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
      meta: { transition: 'custom' }
    },
    {
      path: '/investment-tools',
      name: 'investmenttools',
      component: InvestmentTools,
      meta: { transition: 'custom' }
    },
    {
      path: '/my-profile',
      name: 'myprofile',
      component: MyProfile,
      meta: { transition: 'custom' }
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    return { top: 0 };
  },
})

export default router
