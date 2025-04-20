<template>
	<div class="container mx-auto p-4">
		<div class="bg-base-100 shadow-xl rounded-lg p-6 max-w-2xl mx-auto">
			<h1 class="text-2xl font-bold mb-6">User Profile</h1>
			
			<div v-if="loading || dataLoading" class="flex justify-center my-8">
				<span class="loading loading-spinner loading-lg"></span>
			</div>
			
			<form v-else @submit.prevent="saveProfile" class="space-y-6">
				<div v-if="saveSuccess" class="alert alert-success">
					<svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
					<span>Profile saved successfully!</span>
				</div>
				
				<div v-if="dataError || saveError" class="alert alert-error">
					<svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
					<span>{{ dataError || saveError }}</span>
				</div>
				
				<div class="form-control">
					<label class="label">
						<span class="label-text">Display Name</span>
					</label>
					<input
						type="text"
						v-model="profileData.display_name"
						class="input input-bordered w-full"
						placeholder="Your display name"
					/>
				</div>
				
				<div class="form-control">
					<label class="label">
						<span class="label-text">Bio</span>
					</label>
					<textarea
						v-model="profileData.bio"
						class="textarea textarea-bordered h-24"
						placeholder="Tell us about yourself"
					></textarea>
				</div>
				
				<div class="form-control">
					<label class="label">
						<span class="label-text">Email (can't be changed)</span>
					</label>
					<input
						type="email"
						:value="userEmail"
						class="input input-bordered w-full"
						disabled
					/>
				</div>
				
				<div class="form-control mt-6">
					<button type="submit" class="btn btn-primary" :disabled="saving">
						{{ saving ? 'Saving...' : 'Save Profile' }}
					</button>
				</div>
			</form>
		</div>
	</div>
</template>

<script>
import { mapState, mapGetters } from 'pinia';
import { useAuthStore } from '../stores/auth';
import apiService from '../services/apiService';

export default {
	name: 'ProfileView',
	
	data() {
		return {
			profileData: {
				display_name: '',
				bio: '',
				preferences: {}
			},
			dataLoading: false,
			dataError: null,
			saving: false,
			saveError: null,
			saveSuccess: false
		};
	},
	
	computed: {
		...mapState(useAuthStore, ['user', 'loading']),
		...mapGetters(useAuthStore, ['userEmail'])
	},
	
	created() {
		this.fetchProfile();
	},
	
	methods: {
		async fetchProfile() {
			this.dataLoading = true;
			this.dataError = null;
			
			try {
				const response = await apiService.get('/api/user/profile');
				
				if (response && response.profile) {
					this.profileData = { 
						display_name: response.profile.display_name || '',
						bio: response.profile.bio || '',
						preferences: response.profile.preferences || {}
					};
				}
			} catch (error) {
				this.dataError = error.message;
				console.error('Failed to fetch profile:', error);
			} finally {
				this.dataLoading = false;
			}
		},
		
		async saveProfile() {
			this.saving = true;
			this.saveError = null;
			this.saveSuccess = false;
			
			try {
				await apiService.post('/api/user/profile', this.profileData);
				this.saveSuccess = true;
				
				// Reset success message after 3 seconds
				setTimeout(() => {
					this.saveSuccess = false;
				}, 3000);
			} catch (error) {
				this.saveError = error.message;
				console.error('Failed to save profile:', error);
			} finally {
				this.saving = false;
			}
		}
	}
};
</script>