<!-- src/components/Navbar.vue -->
<template>
	<header class="bg-gradient-to-r from-purple-700 to-indigo-800 text-white shadow-lg">
		<div class="container mx-auto">
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
					<router-link to="/" class="flex items-center gap-3">
						<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-8 h-8">
							<path d="M18.375 2.25c-1.035 0-1.875.84-1.875 1.875v15.75c0 1.035.84 1.875 1.875 1.875h.75c1.035 0 1.875-.84 1.875-1.875V4.125c0-1.036-.84-1.875-1.875-1.875h-.75zM9.75 8.625c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v11.25c0 1.035-.84 1.875-1.875 1.875h-.75a1.875 1.875 0 01-1.875-1.875V8.625zM3 13.125c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v6.75c0 1.035-.84 1.875-1.875 1.875h-.75A1.875 1.875 0 013 19.875v-6.75z" />
						</svg>
						<span class="font-bold text-xl tracking-tight">TokenLabs</span>
					</router-link>
				</div>
				
				<!-- Desktop menu -->
				<div class="flex-none hidden lg:block">
					<ul class="menu menu-horizontal gap-2">
						<li><router-link to="/" class="btn btn-ghost normal-case">Dashboard</router-link></li>
						<li v-if="user"><router-link to="/dashboard-builder" class="btn btn-ghost normal-case">Build</router-link></li>
						<li><a href="#" class="btn btn-ghost normal-case">About</a></li>
					</ul>
				</div>
				
				<!-- Right-side items -->
				<div class="flex-none gap-2">
					<div v-if="loading" class="flex items-center">
						<span class="loading loading-spinner loading-sm text-primary"></span>
					</div>
					<template v-else-if="user">
						<div class="dropdown dropdown-end">
							<div tabindex="0" role="button" class="flex items-center gap-2 btn btn-ghost">
								<div class="avatar">
									<div class="w-8 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2">
										<img :src="userPhotoURL || 'https://i.pravatar.cc/300'" alt="User avatar" />
									</div>
								</div>
								<span class="hidden md:inline-block">{{ user.displayName || user.email }}</span>
								<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
								</svg>
							</div>
							<ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52 text-base-content">
								<li>
									<router-link to="/profile" class="flex items-center gap-2">
										<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
											<path stroke-linecap="round" stroke-linejoin="round" d="M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z" />
										</svg>
										My Profile
									</router-link>
								</li>
								<li>
									<router-link to="/saved-reports" class="flex items-center gap-2">
										<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
											<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
										</svg>
										My Dashboards
									</router-link>
								</li>
								<div class="divider my-1"></div>
								<li>
									<a @click="handleLogout" class="flex items-center gap-2 text-error">
										<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
											<path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
										</svg>
										Logout
									</a>
								</li>
							</ul>
						</div>
					</template>
					<template v-else>
						<router-link to="/login" class="btn btn-outline btn-sm text-white border-white hover:bg-white hover:text-primary">Login</router-link>
						<router-link to="/register" class="btn btn-primary btn-sm">Sign Up</router-link>
					</template>
				</div>
			</div>
		</div>
	</header>
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