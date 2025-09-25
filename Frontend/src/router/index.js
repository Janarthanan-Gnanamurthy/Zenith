// router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import DataProcessor from '../components/DataProcessor.vue';
import DashboardBuilder from '../components/DashboardBuilder.vue';
import Register from '@/components/Register.vue';
import Login from '../components/login.vue';
import { useAuthStore } from '../stores/authStore.js'

const routes = [
  {
    path: '/',
    name: 'DataProcessor',
    component: DataProcessor,
    meta: { requiresAuth: true} 
  },
  {
    path: '/dashboard-builder',
    name: 'DashboardBuilder',
    component: DashboardBuilder,
    meta: { requiresAuth: false } 
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true } 
  },
  { 
    path: '/login', 
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/components/About.vue')
  },
  {
    path: '/saved-reports',
    name: 'SavedReports',
    component: () => import('@/components/SavedReports.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
      name: 'Settings',
    component: () => import('@/components/InProgress.vue'),
    props: {
      pageName: 'Settings',
      completionDate: 'April 25, 2025',
      defaultProgress: 95
    },
  },
  {
    path: '/support',
      name: 'support',
    component: () => import('@/components/InProgress.vue'),
    props: {
      pageName: 'support',
      completionDate: 'April 25, 2025',
      defaultProgress: 20
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});


router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  
  // Wait for auth to initialize if it hasn't already
  if (authStore.loading) {
    await authStore.initialize();
  }
  
  const isLoggedIn = !!authStore.user;
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login');
  } else if (to.meta.requiresGuest && isLoggedIn) {
    next({ name: 'DataProcessor' });
  } else {
    next();
  }
});

export default router;
