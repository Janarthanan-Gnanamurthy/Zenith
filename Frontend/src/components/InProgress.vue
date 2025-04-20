<!-- src/components/UnderConstruction.vue -->
<template>
    <div class="flex min-h-screen">      
      <!-- Right side - Under Construction message -->
      <div class="w-full flex items-center justify-center p-8">
        <div class="w-full max-w-md">
          <div class="text-center mb-10 lg:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-16 h-16 mx-auto text-primary">
              <path d="M18.375 2.25c-1.035 0-1.875.84-1.875 1.875v15.75c0 1.035.84 1.875 1.875 1.875h.75c1.035 0 1.875-.84 1.875-1.875V4.125c0-1.036-.84-1.875-1.875-1.875h-.75zM9.75 8.625c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v11.25c0 1.035-.84 1.875-1.875 1.875h-.75a1.875 1.875 0 01-1.875-1.875V8.625zM3 13.125c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v6.75c0 1.035-.84 1.875-1.875 1.875h-.75A1.875 1.875 0 013 19.875v-6.75z" />
            </svg>
            <h1 class="text-2xl font-bold mt-2">DataViz Pro</h1>
          </div>
          
          <div class="text-center mb-8">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24 mx-auto text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
          </div>
          
          <h2 class="text-3xl font-extrabold mb-4 text-center">{{ pageName || 'Page' }} Under Development</h2>
          <p class="text-base-content/60 mb-6 text-center">We're working hard to bring you an amazing experience. This page will be available soon!</p>
          
          <div class="bg-base-200 rounded-lg p-6 mb-8 shadow-md">
            <div class="flex items-center mb-4">
              <div class="h-4 w-4 rounded-full bg-primary animate-pulse mr-2"></div>
              <p class="font-medium">Development in progress</p>
            </div>
            <div class="w-full bg-base-300 rounded-full h-2.5">
              <div class="bg-primary h-2.5 rounded-full" :style="`width: ${progressValue}%`"></div>
            </div>
            <p class="text-right text-sm mt-2 text-base-content/60">{{ progressValue }}% Complete</p>
          </div>
          
          <div class="text-center space-y-4">
            <p class="text-base-content/70">Expected completion date: {{ completionDate || 'Coming Soon' }}</p>
            
            <button 
              @click="goBack" 
              class="btn btn-primary btn-outline w-full gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  
  const props = defineProps({
    pageName: {
      type: String,
      default: ''
    },
    completionDate: {
      type: String,
      default: ''
    },
    defaultProgress: {
      type: Number,
      default: 65
    }
  });
  
  const router = useRouter();
  const route = useRoute();
  
  // Calculate progress value from query parameter or use default
  const progressValue = computed(() => {
    // Check if progress exists in query parameters
    if (route.query.progress) {
      // Parse the query parameter as integer
      const queryProgress = parseInt(route.query.progress);
      
      // Validate the progress is within bounds (0-100)
      if (!isNaN(queryProgress) && queryProgress >= 0 && queryProgress <= 100) {
        return queryProgress;
      }
    }
    
    // If no valid query parameter exists, use the default progress
    return props.defaultProgress;
  });
  
  const goBack = () => {
    router.go(-1);
  };
  </script>