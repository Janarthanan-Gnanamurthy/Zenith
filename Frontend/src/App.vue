<template>
  <div class="drawer lg:drawer-open">
    <!-- Drawer toggle -->
    <input id="main-drawer" type="checkbox" class="drawer-toggle" />
    
    <!-- Main content -->
    <div class="drawer-content flex flex-col bg-gray-50">
      <!-- Navbar - only show when authenticated and make it sticky -->
      <header v-if="isAuthenticated" class="bg-gradient-to-r from-purple-700 to-indigo-800 text-white shadow-lg sticky top-0 z-10">
        <div class="">
          <div class="navbar px-4">
            <!-- Mobile menu button -->
            <div class="flex-none lg:hidden">
              <label for="main-drawer" class="btn btn-square btn-ghost text-white">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-6 h-6 stroke-current">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                </svg>
              </label>
            </div>
            
            <!-- Brand logo -->
            <div class="flex-1">
              <router-link to="/" class="flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-8 h-8">
                  <path d="M18.375 2.25c-1.035 0-1.875.84-1.875 1.875v15.75c0 1.035.84 1.875 1.875 1.875h.75c1.035 0 1.875-.84 1.875-1.875V4.125c0-1.036-.84-1.875-1.875-1.875h-.75zM9.75 8.625c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v11.25c0 1.035-.84 1.875-1.875 1.875h-.75a1.875 1.875 0 01-1.875-1.875V8.625zM3 13.125c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v6.75c0 1.035-.84 1.875-1.875 1.875h-.75A1.875 1.875 0 013 19.875v-6.75z" />
                </svg>
                <span class="font-bold text-xl tracking-tight">TokenLabs</span>
              </router-link>
            </div>
            
            <!-- Desktop menu -->
            <div class="flex-none hidden lg:block">
              <ul class="menu menu-horizontal gap-2 py-0">
                <li><router-link to="/" class="btn btn-ghost normal-case py-0">Dashboard</router-link></li>
                <li><router-link to="/dashboard-builder" class="btn btn-ghost normal-case py-0">Build</router-link></li>
                <li><router-link to="/about" class="btn btn-ghost normal-case py-0">About</router-link></li>
              </ul>
            </div>
          </div>
        </div>
      </header>
      
      <!-- Page Content -->
      <router-view />
    </div>
    
    <!-- Sidebar drawer - only show when authenticated -->
    <div v-if="isAuthenticated" class="drawer-side">
      <label for="main-drawer" class="drawer-overlay"></label>
      <aside class="bg-base-100 w-50 h-full border-r">
        <!-- User information section instead of duplicating project name -->
        <div class="p-4 flex items-center gap-3 border-b">
          <div class="avatar">
            <div class="w-10 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2">
              <img :src="userPhotoURL || 'https://i.pravatar.cc/300'" alt="User avatar" />
            </div>
          </div>
          <div class="flex flex-col">
            <span class="font-medium">{{ authStore.user ? (authStore.user.displayName || 'User') : 'Guest' }}</span>
            <span class="text-xs text-gray-500">{{ authStore.user ? authStore.user.email : '' }}</span>
          </div>
        </div>
        
        <ul class="menu p-4 text-base-content">
          <li class="menu-title">Main Navigation</li>
          <li>
            <router-link to="/">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Data Analysis
            </router-link>
          </li>
          <li>
            <router-link to="/dashboard-builder">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
              Dashboard Builder
            </router-link>
          </li>
          <li>
              <router-link to="/saved-reports">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Saved Reports
              </router-link>
          </li>
          
          <li class="menu-title mt-4">Tools</li>
          <li>
            <router-link to="/settings">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Settings
            </router-link>
          </li>
          <li>
            <router-link to="/support">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Help & Support
            </router-link>
          </li> 
        </ul>
        
        <div class="absolute bottom-0 w-full p-4 border-t">
          <!-- Logout button -->
          <button 
            @click="handleLogout" 
            class="btn btn-outline btn-error btn-block mb-2 items-center justify-center gap-2 text-xs"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
            </svg>
            Logout
          </button>
          
          <div class="text-xs text-base-content/60 mb-2 uppercase font-semibold">Current Version</div>
          <div class="flex justify-between items-center">
            <span class="badge badge-primary text-xs text-white">v2.0.3</span>
            <a href="#" class="link link-hover text-sm">Check for updates</a>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useAuthStore } from './stores/authStore';
import { useRouter } from 'vue-router';

export default {
  name: "App",
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    
    // Check if user is authenticated
    const isAuthenticated = computed(() => !!authStore.user);
    
    // Computed property for user photo URL
    const userPhotoURL = computed(() => {
      return authStore.user && authStore.user.photoURL ? authStore.user.photoURL : null;
    });
    
    // Handle user logout
    const handleLogout = async () => {
      await authStore.logout();
      router.push('/login');
    };
    
    return {
      authStore,
      isAuthenticated,
      userPhotoURL,
      handleLogout
    };
  }
};
</script>

<style>
/* Global styles */
* {
  font-family: 'Inter', sans-serif;
}

.drawer-toggle:checked ~ .drawer-side > .drawer-overlay {
  background-color: rgba(0, 0, 0, 0.4);
}
</style>