<template>
    <div class="min-h-screen bg-gray-50">
        <div class="container mx-auto px-4 py-8 sm:px-6 lg:px-8">
            <!-- Header -->
            <div class="flex justify-between items-center mb-8">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">Saved Dashboards</h1>
                    <p class="text-gray-600 mt-2">Manage and load your previously saved dashboards</p>
                </div>
                <button 
                    @click="refreshDashboards" 
                    class="btn btn-outline btn-primary"
                    :disabled="loading"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Refresh
                </button>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="flex justify-center items-center py-12">
                <div class="loading loading-spinner loading-lg text-primary"></div>
            </div>

            <!-- Not Logged In -->
            <div v-else-if="!user" class="text-center py-12">
                <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-8 max-w-md mx-auto">
                    <div class="text-primary mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">Authentication Required</h3>
                    <p class="text-gray-600 mb-6">Please log in to view your saved dashboards.</p>
                    <button @click="$router.push('/login')" class="btn btn-primary">
                        Go to Login
                    </button>
                </div>
            </div>

            <!-- Empty State -->
            <div v-else-if="dashboards.length === 0" class="text-center py-12">
                <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-8 max-w-md mx-auto">
                    <div class="text-gray-400 mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">No Dashboards Yet</h3>
                    <p class="text-gray-600 mb-6">Create your first dashboard to get started.</p>
                    <button @click="$router.push('/dashboard-builder')" class="btn btn-primary">
                        Create Dashboard
                    </button>
                </div>
            </div>

            <!-- Dashboard Grid -->
            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div 
                    v-for="dashboard in dashboards" 
                    :key="dashboard.id" 
                    class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all duration-200"
                >
                    <!-- Dashboard Header -->
                    <div class="p-6 border-b border-gray-100">
                        <div class="flex items-start justify-between">
                            <div class="flex-1 min-w-0">
                                <h3 class="text-lg font-semibold text-gray-900 truncate">{{ dashboard.name }}</h3>
                                <p class="text-sm text-gray-500 mt-1">{{ dashboard.description || 'No description' }}</p>
                            </div>
                            <div class="flex items-center gap-2 ml-4">
                                <span class="badge badge-primary badge-sm">
                                    {{ dashboard.widgets?.length || 0 }} widget{{ (dashboard.widgets?.length || 0) !== 1 ? 's' : '' }}
                                </span>
                            </div>
                        </div>
                    </div>

                    <!-- Dashboard Info -->
                    <div class="p-6">
                        <div class="space-y-3">
                            <div class="flex items-center text-sm text-gray-500">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                Created: {{ formatDate(dashboard.createdAt) }}
                            </div>
                            <div v-if="dashboard.updatedAt && dashboard.updatedAt !== dashboard.createdAt" class="flex items-center text-sm text-gray-500">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                                Updated: {{ formatDate(dashboard.updatedAt) }}
                            </div>
                        </div>
                    </div>

                    <!-- Actions -->
                    <div class="px-6 py-4 bg-gray-50 flex justify-between items-center">
                        <button 
                            @click="loadDashboard(dashboard)" 
                            class="btn btn-primary btn-sm"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                            </svg>
                            Load Dashboard
                        </button>
                        <div class="flex gap-2">
                            <button 
                                @click="duplicateDashboard(dashboard)" 
                                class="btn btn-ghost btn-sm"
                                title="Duplicate"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                            </button>
                            <button 
                                @click="deleteDashboard(dashboard)" 
                                class="btn btn-ghost btn-sm text-error hover:bg-error hover:text-white"
                                title="Delete"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from '@/firebase.js'; 
import { useDataStore } from '@/stores/datasetStore';
import { dashboardService } from '@/services/dashboardService';

export default {
    data() {
        return {
            dashboards: [],
            loading: true,
            user: null
        };
    },
    async mounted() {
        // Listen for auth state changes
        onAuthStateChanged(auth, async (user) => {
            this.user = user;
            if (user) {
                await this.loadDashboards();
            } else {
                this.loading = false;
            }
        });
    },
    methods: {
        async loadDashboards() {
            this.loading = true;
            try {
                this.dashboards = await dashboardService.getDashboards();
            } catch (error) {
                console.error('Error loading dashboards:', error);
                alert('Failed to load dashboards. Please try again.');
            } finally {
                this.loading = false;
            }
        },

        async refreshDashboards() {
            await this.loadDashboards();
        },

        loadDashboard(dashboard) {
            const dataStore = useDataStore();
            dataStore.setHeaders(dashboard.headers);
            dataStore.setRows(dashboard.rows);
            localStorage.setItem('dashboardLayout', JSON.stringify(dashboard.widgets));
            this.$router.push({ name: 'DashboardBuilder' });
        },

        async duplicateDashboard(dashboard) {
            try {
                const duplicatedData = {
                    name: `${dashboard.name} (Copy)`,
                    widgets: JSON.parse(JSON.stringify(dashboard.widgets)),
                    headers: [...dashboard.headers],
                    rows: dashboard.rows.map(row => [...row]),
                    description: `Copy of ${dashboard.name}`
                };
                
                await dashboardService.saveDashboard(duplicatedData);
                await this.loadDashboards();
                alert('Dashboard duplicated successfully!');
            } catch (error) {
                console.error('Error duplicating dashboard:', error);
                alert('Failed to duplicate dashboard. Please try again.');
            }
        },

        async deleteDashboard(dashboard) {
            if (!confirm(`Are you sure you want to delete "${dashboard.name}"? This action cannot be undone.`)) {
                return;
            }

            try {
                await dashboardService.deleteDashboard(dashboard.id);
                await this.loadDashboards();
                alert('Dashboard deleted successfully!');
            } catch (error) {
                console.error('Error deleting dashboard:', error);
                alert('Failed to delete dashboard. Please try again.');
            }
        },

        formatDate(timestamp) {
            if (!timestamp) return 'Unknown';
            
            let date;
            if (timestamp.toDate) {
                // Firestore timestamp
                date = timestamp.toDate();
            } else if (timestamp instanceof Date) {
                // Regular Date object
                date = timestamp;
            } else {
                // Try to parse as date
                date = new Date(timestamp);
            }
            
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
};
</script>