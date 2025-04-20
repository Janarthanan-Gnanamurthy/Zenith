import { defineStore } from 'pinia';
import { ref } from 'vue';
import { authService } from '../services/authService';
import { apiClient } from '../services/apiService';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const loading = ref(true);
  const error = ref(null);

  async function initialize() {
    loading.value = true;
    try {
      user.value = await authService.getCurrentUser();
      if (user.value) {
        // Verify token with backend
        await apiClient.post('http://127.0.0.1:8000/api/auth/verify-token');
      }
    } catch (err) {
      console.error('Auth initialization error:', err);
      error.value = err.message;
      user.value = null;
    } finally {
      loading.value = false;
    }
  }

  async function register(email, password) {
    loading.value = true;
    error.value = null;
    try {
      const newUser = await authService.register(email, password);
      user.value = newUser;
      // Create user profile in backend
      await apiClient.post('http://127.0.0.1:8000/api/user/profile');
      return newUser;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function login(email, password) {
    loading.value = true;
    error.value = null;
    try {
      const loggedInUser = await authService.login(email, password);
      user.value = loggedInUser;
      return loggedInUser;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function loginWithGoogle() {
    loading.value = true;
    error.value = null;
    try {
      const loggedInUser = await authService.loginWithGoogle();
      user.value = loggedInUser;
      // Check if it's a new user and create profile if needed
      await apiClient.post('http://127.0.0.1:8000/api/user/profile');
      return loggedInUser;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    loading.value = true;
    try {
      await authService.logout();
      user.value = null;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  }

  return {
    user,
    loading,
    error,
    initialize,
    register,
    login,
    loginWithGoogle,
    logout
  };
});