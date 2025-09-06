<!-- src/components/login.vue -->
<template>
  <div class="flex min-h-screen">
    <!-- Left side - Background image -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-tr from-purple-800 to-indigo-600 items-center justify-center p-12">
      <div class="max-w-xl text-center">
        <div class="mb-8">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white" class="w-24 h-24 mx-auto">
            <path d="M18.375 2.25c-1.035 0-1.875.84-1.875 1.875v15.75c0 1.035.84 1.875 1.875 1.875h.75c1.035 0 1.875-.84 1.875-1.875V4.125c0-1.036-.84-1.875-1.875-1.875h-.75zM9.75 8.625c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v11.25c0 1.035-.84 1.875-1.875 1.875h-.75a1.875 1.875 0 01-1.875-1.875V8.625zM3 13.125c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v6.75c0 1.035-.84 1.875-1.875 1.875h-.75A1.875 1.875 0 013 19.875v-6.75z" />
          </svg>
          <h1 class="text-4xl font-bold text-white mt-5">TokenLabs</h1>
        </div>
        <h2 class="text-2xl font-semibold text-white">Transform Your Data Into Powerful Visualizations</h2>
        <p class="text-indigo-100 mt-4 text-lg">Unlock insights with AI-powered analytics and beautiful interactive dashboards</p>
        <div class="mt-12 grid grid-cols-3 gap-4">
          <div class="bg-white/10 p-4 rounded-lg backdrop-blur-sm">
            <div class="text-white text-4xl font-bold">20+</div>
            <div class="text-indigo-100 text-sm">Chart Types</div>
          </div>
          <div class="bg-white/10 p-4 rounded-lg backdrop-blur-sm">
            <div class="text-white text-4xl font-bold">65%</div>
            <div class="text-indigo-100 text-sm">More effecient</div>
          </div>
          <div class="bg-white/10 p-4 rounded-lg backdrop-blur-sm">
            <div class="text-white text-4xl font-bold">99.99%</div>
            <div class="text-indigo-100 text-sm">Satisfaction</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Right side - Login form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8">
      <div class="w-full max-w-md">
        <div class="text-center mb-10 lg:hidden">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-16 h-16 mx-auto text-primary">
            <path d="M18.375 2.25c-1.035 0-1.875.84-1.875 1.875v15.75c0 1.035.84 1.875 1.875 1.875h.75c1.035 0 1.875-.84 1.875-1.875V4.125c0-1.036-.84-1.875-1.875-1.875h-.75zM9.75 8.625c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v11.25c0 1.035-.84 1.875-1.875 1.875h-.75a1.875 1.875 0 01-1.875-1.875V8.625zM3 13.125c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v6.75c0 1.035-.84 1.875-1.875 1.875h-.75A1.875 1.875 0 013 19.875v-6.75z" />
          </svg>
          <h1 class="text-2xl font-bold mt-2">DataViz Pro</h1>
        </div>
        
        <h2 class="text-3xl font-extrabold mb-2">Welcome back</h2>
        <p class="text-base-content/60 mb-8">Please sign in to your account</p>
        
        <div v-if="authStore.error" class="alert alert-error mb-6 shadow-md">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span>{{ authStore.error }}</span>
        </div>
        
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Email</span>
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              </div>
              <input 
                type="email" 
                v-model="email" 
                placeholder="Enter your email address" 
                class="input input-bordered w-full pl-10" 
                required
              />
            </div>
          </div>
          
          <div class="form-control">
            <div class="flex items-center justify-between">
              <label class="label">
                <span class="label-text font-medium">Password</span>
              </label>
              <a href="#" class="text-sm text-primary hover:underline">Forgot password?</a>
            </div>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <input 
                type="password" 
                v-model="password" 
                placeholder="Enter your password" 
                class="input input-bordered w-full pl-10" 
                required
              />
            </div>
          </div>
          
          <div class="form-control">
            <label class="cursor-pointer label justify-start gap-2">
              <input type="checkbox" class="checkbox checkbox-primary checkbox-sm" />
              <span class="label-text">Keep me signed in</span>
            </label>
          </div>
          
          <button 
            type="submit" 
            class="btn btn-primary w-full" 
            :disabled="authStore.loading"
          >
            <span v-if="authStore.loading" class="loading loading-spinner loading-sm"></span>
            <span>Sign In</span>
          </button>
        </form>
        
        <div class="divider my-8">OR</div>
        
        <button 
          @click="handleGoogleLogin" 
          class="btn btn-outline w-full gap-2" 
          :disabled="authStore.loading"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" preserveAspectRatio="xMidYMid" viewBox="0 0 256 262">
            <path fill="#4285F4" d="M255.878 133.451c0-10.734-.871-18.567-2.756-26.69H130.55v48.448h71.947c-1.45 12.04-9.283 30.172-26.69 42.356l-.244 1.622 38.755 30.023 2.685.268c24.659-22.774 38.875-56.282 38.875-96.027"></path>
            <path fill="#34A853" d="M130.55 261.1c35.248 0 64.839-11.605 86.453-31.622l-41.196-31.913c-11.024 7.688-25.82 13.055-45.257 13.055-34.523 0-63.824-22.773-74.269-54.25l-1.531.13-40.298 31.187-.527 1.465C35.393 231.798 79.49 261.1 130.55 261.1"></path>
            <path fill="#FBBC05" d="M56.281 156.37c-2.756-8.123-4.351-16.827-4.351-25.82 0-8.994 1.595-17.697 4.206-25.82l-.073-1.73L15.26 71.312l-1.335.635C5.077 89.644 0 109.517 0 130.55s5.077 40.905 13.925 58.602l42.356-32.782"></path>
            <path fill="#EB4335" d="M130.55 50.479c24.514 0 41.05 10.589 50.479 19.438l36.844-35.974C195.245 12.91 165.798 0 130.55 0 79.49 0 35.393 29.301 13.925 71.947l42.211 32.783c10.59-31.477 39.891-54.251 74.414-54.251"></path>
          </svg>
          Continue with Google
        </button>
        
        <div class="text-center mt-8">
          <span class="text-base-content/70">Don't have an account?</span>
          <router-link to="/register" class="text-primary font-medium hover:underline ml-1">Create account</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore.js';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');

const handleLogin = async () => {
  try {
    await authStore.login(email.value, password.value);
    router.push('/');
  } catch (error) {
    // Error is already handled in the store
  }
};

const handleGoogleLogin = async () => {
  try {
    await authStore.loginWithGoogle();
    router.push('/');
  } catch (error) {
    // Error is already handled in the store
  }
};
</script>