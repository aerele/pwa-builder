import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    name: 'Login',
    path: '/login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    name: 'SignUp',
    path: '/signup',
    component: () => import('@/pages/SignUp.vue'),
  },
  {
    name: 'ForgetPassword',
    path: '/forget-password',
    component: () => import('@/pages/ForgetPassword.vue'),
  },
  {
    name: 'Builder',
    path: '/builder',
    component: () => import('@/pages/builder/Builder.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/frontend'),
  routes,
})

// router.beforeEach(async (to, from, next) => {
//   let isLoggedIn = session.isLoggedIn
//   try {
//     await userResource.promise
//   } catch (error) {
//     isLoggedIn = false
//   }

//   if (to.name === 'Login' && isLoggedIn) {
//     next({ name: 'Home' });
//   } else if (to.name === 'ForgetPassword' || to.name === 'Login' || to.name === 'SignUp' || isLoggedIn) {
//     next();
//   } else {
//     next({ name: 'Login'});
//   }
// });

export default router
