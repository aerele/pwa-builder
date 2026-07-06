import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'
import AppShell from '@/shell/AppShell.vue'

const routes = [
  // --- Auth (bare, no shell) ---
  { name: 'Login', path: '/login', meta: { public: true }, component: () => import('@/pages/Login.vue') },
  { name: 'SignUp', path: '/signup', meta: { public: true }, component: () => import('@/pages/SignUp.vue') },
  {
    name: 'ForgetPassword',
    path: '/forget-password',
    meta: { public: true },
    component: () => import('@/pages/ForgetPassword.vue'),
  },

  // --- App (wrapped in AppShell; rail switches on :projectId) ---
  {
    path: '/',
    component: AppShell,
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/pages/Dashboard.vue') },
      { path: 'templates', name: 'Templates', component: () => import('@/pages/Templates.vue') },
      { path: 'settings', name: 'Settings', component: () => import('@/pages/Settings.vue') },

      // Project workspace (flattened so AppShell sees :projectId and shows ProjectRail)
      { path: 'p/:projectId', redirect: (to) => ({ name: 'ProjectOverview', params: to.params }) },
      { path: 'p/:projectId/overview', name: 'ProjectOverview', props: true, component: () => import('@/pages/project/ProjectOverview.vue') },
      { path: 'p/:projectId/data', name: 'ProjectData', props: true, component: () => import('@/pages/project/ProjectData.vue') },
      { path: 'p/:projectId/screens', name: 'ProjectScreens', props: true, component: () => import('@/pages/project/ProjectScreens.vue') },
      // Phase 2 three-pane builder (palette · canvas · live preview).
      { path: 'p/:projectId/screens/:screenId?/build', name: 'ProjectBuilder', props: true, component: () => import('@/pages/builder/Builder.vue') },
      { path: 'p/:projectId/flow', name: 'ProjectFlow', props: true, component: () => import('@/pages/project/ProjectFlow.vue') },
      { path: 'p/:projectId/publish', name: 'ProjectPublish', props: true, component: () => import('@/pages/project/ProjectPublish.vue') },
    ],
  },

  // --- Legacy redirects (keep old links alive during migration) ---
  { path: '/builder', redirect: { name: 'Dashboard' } },
  { path: '/builder/:id', redirect: (to) => ({ name: 'ProjectOverview', params: { projectId: to.params.id } }) },

  // Fallback
  { path: '/:pathMatch(.*)*', redirect: { name: 'Dashboard' } },
]

const router = createRouter({
  history: createWebHistory('/pwa-builder'),
  routes,
})

// Auth guard (re-enabled). Public routes always allowed; everything else
// requires a logged-in session.
router.beforeEach(async (to, from, next) => {
  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.meta.public) {
    // Bounce logged-in users away from auth pages.
    return isLoggedIn ? next({ name: 'Dashboard' }) : next()
  }
  return isLoggedIn ? next() : next({ name: 'Login' })
})

export default router
