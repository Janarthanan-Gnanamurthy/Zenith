<!-- <template>
	<div class="container mx-auto p-4">
		<div class="bg-base-100 shadow-xl rounded-lg p-6">
			<h1 class="text-2xl font-bold mb-6">Dashboard</h1>
			
			<div v-if="loading" class="flex justify-center">
				<span class="loading loading-spinner loading-lg"></span>
			</div>
			
			<div v-else>
				<div class="card bg-base-200 mb-6">
					<div class="card-body">
						<h2 class="card-title">Welcome, {{ welcomeName }}!</h2>
						<p>This is your protected dashboard. Only authenticated users can see this page.</p>
					</div>
				</div>
				
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div class="card bg-primary text-primary-content">
						<div class="card-body">
							<h3 class="card-title">User Information</h3>
							<p><strong>Email:</strong> {{ userEmail }}</p>
							<p><strong>ID:</strong> {{ userId }}</p>
							<p><strong>Email Verified:</strong> {{ emailVerified ? 'Yes' : 'No' }}</p>
						</div>
					</div>
					
					<div class="card bg-secondary text-secondary-content">
						<div class="card-body">
							<h3 class="card-title">Actions</h3>
							<div class="card-actions justify-end">
								<button @click="fetchUserData" class="btn">Refresh Data</button>
								<router-link to="/profile" class="btn btn-outline">Edit Profile</router-link>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { mapState, mapGetters } from 'pinia';
import { useAuthStore } from '../stores/authStore';
import { apiClient }from '../services/apiService';

export default {
	name: 'DashboardView',
	
	data() {
		return {
			userData: null,
			dataLoading: false,
			dataError: null
		};
	},
	
	computed: {
		...mapState(useAuthStore, ['user', 'loading']),
		...mapGetters(useAuthStore, ['userEmail']),
		
		userId() {
			return this.user ? this.user.uid : 'Unknown';
		},
		
		emailVerified() {
			return this.user ? this.user.emailVerified : false;
		},
		
		welcomeName() {
			if (this.user && this.user.displayName) {
				return this.user.displayName;
			}
			
			if (this.userData && this.userData.profile && this.userData.profile.display_name) {
				return this.userData.profile.display_name;
			}
			
			return this.userEmail ? this.userEmail.split('@')[0] : 'User';
		}
	},
	
	created() {
		this.fetchUserData();
	},
	
	methods: {
		async fetchUserData() {
			this.dataLoading = true;
			this.dataError = null;
			
			try {
				this.userData = await apiClient.get('/api/user/profile');
			} catch (error) {
				this.dataError = error.message;
				console.error('Failed to fetch user data:', error);
			} finally {
				this.dataLoading = false;
			}
		}
	}
};
</script> -->