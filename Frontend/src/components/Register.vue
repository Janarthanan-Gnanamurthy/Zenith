<template>
	<div class="min-h-screen flex items-center justify-center bg-base-200">
		<div class="card w-96 bg-base-100 shadow-xl">
			<div class="card-body">
				<h2 class="card-title text-center">Create an Account</h2>
				
				<div v-if="authStore.error" class="alert alert-error">
					{{ authStore.error }}
				</div>
				
				<form @submit.prevent="handleRegister">
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
					
					<div class="form-control w-full mb-4">
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
						<label class="label">
							<span class="label-text-alt text-gray-500">Password must be at least 6 characters</span>
						</label>
					</div>
					
					<div class="form-control w-full mb-6">
						<label class="label">
							<span class="label-text">Confirm Password</span>
						</label>
						<input 
							type="password" 
							v-model="confirmPassword" 
							placeholder="Confirm your password" 
							class="input input-bordered w-full" 
							required
						/>
						<label class="label" v-if="passwordMismatch">
							<span class="label-text-alt text-error">Passwords do not match</span>
						</label>
					</div>
					
					<button 
						type="submit" 
						class="btn btn-primary w-full" 
						:disabled="authStore.loading || passwordMismatch"
					>
						<span v-if="authStore.loading">Creating account...</span>
						<span v-else>Register</span>
					</button>
				</form>
				
				<div class="divider">OR</div>
				
				<button 
					@click="handleGoogleSignup" 
					class="btn btn-outline w-full" 
					:disabled="authStore.loading"
				>
					Continue with Google
				</button>
				
				<div class="mt-4 text-center">
					Already have an account? 
					<router-link to="/login" class="link link-primary">Login</router-link>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const confirmPassword = ref('');

const passwordMismatch = computed(() => {
	return confirmPassword.value && password.value !== confirmPassword.value;
});

const handleRegister = async () => {
	if (passwordMismatch.value) {
		return;
	}
	
	try {
		await authStore.register(email.value, password.value);
		router.push('/');
	} catch (error) {
		// Error is already handled in the store
	}
};

const handleGoogleSignup = async () => {
	try {
		await authStore.loginWithGoogle();
		router.push('/');
	} catch (error) {
		// Error is already handled in the store
	}
};
</script>