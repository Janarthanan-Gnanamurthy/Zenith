<!-- src/views/Login.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-base-200">
    <div class="card w-96 bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-center">Login</h2>
        
        <div v-if="authStore.error" class="alert alert-error">
          {{ authStore.error }}
        </div>
        
        <form @submit.prevent="handleLogin">
          <div class="form-control w-full mb-4">
            <label class="label">
              <span class="label-text">Email</span>
            </label>
            <input 
              type="email" 
              v-model="email" 
              placeholder="Enter your email" 
              class="input input-bordered w-full" 
              required
            />
          </div>
          
          <div class="form-control w-full mb-6">
            <label class="label">
              <span class="label-text">Password</span>
            </label>
            <input 
              type="password" 
              v-model="password" 
              placeholder="Enter your password" 
              class="input input-bordered w-full" 
              required
            />
          </div>
          
          <button 
            type="submit" 
            class="btn btn-primary w-full" 
            :disabled="authStore.loading"
          >
            <span v-if="authStore.loading">Loading...</span>
            <span v-else>Login</span>
          </button>
        </form>
        
        <div class="divider">OR</div>
        
        <button 
          @click="handleGoogleLogin" 
          class="btn btn-outline w-full" 
          :disabled="authStore.loading"
        >
          Continue with Google
        </button>
        
        <div class="mt-4 text-center">
          Don't have an account? 
          <router-link to="/register" class="link link-primary">Register</router-link>
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