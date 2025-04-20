<!-- src/components/Navbar.vue -->
<template>
	<div class="navbar bg-base-100 shadow-lg">
		<div class="navbar-start">
			<router-link to="/" class="btn btn-ghost normal-case text-xl">Datafy</router-link>
		</div>
		
		<div class="navbar-center hidden lg:flex">
			<ul class="menu menu-horizontal px-1">
				<li><router-link to="/">Home</router-link></li>
				<li v-if="user"><router-link to="/dashboard">Dashboard</router-link></li>
			</ul>
		</div>
		
		<div class="navbar-end">
			<div v-if="loading">
				<span class="loading loading-spinner"></span>
			</div>
			<template v-else-if="user">
				<div class="dropdown dropdown-end">
					<label tabindex="0" class="btn btn-ghost btn-circle avatar">
						<div class="w-10 rounded-full">
							<img :src="userPhotoURL || 'https://i.pravatar.cc/300'" />
						</div>
					</label>
					<ul tabindex="0" class="mt-3 p-2 shadow menu menu-compact dropdown-content bg-base-100 rounded-box w-52">
						<li><router-link to="/profile">Profile</router-link></li>
						<li><a @click="handleLogout">Logout</a></li>
					</ul>
				</div>
			</template>
			<template v-else>
				<router-link to="/login" class="btn btn-sm">Login</router-link>
				<router-link to="/register" class="btn btn-sm btn-primary ml-2">Register</router-link>
			</template>
		</div>
	</div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'pinia';
import { useAuthStore } from '../stores/authStore';

export default {
	name: 'NavBar',
	
	computed: {
		...mapState(useAuthStore, ['user', 'loading']),
		...mapGetters(useAuthStore, ['userPhotoURL'])
	},
	
	methods: {
		...mapActions(useAuthStore, ['logout']),
		
		async handleLogout() {
			await this.logout();
			this.$router.push('/login');
		}
	}
};
</script>