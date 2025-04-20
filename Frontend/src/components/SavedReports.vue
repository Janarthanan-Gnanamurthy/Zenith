<template>
    <div class="container mx-auto py-8">
        <h1 class="text-2xl font-bold mb-6">Saved Dashboards</h1>
        <div v-if="!user" class="text-center text-gray-500">Please log in to view your saved dashboards.</div>
        <div v-else>
            <div v-if="loading" class="text-center">Loading...</div>
            <div v-else-if="dashboards.length === 0" class="text-center text-gray-500">No dashboards saved yet.</div>
            <div v-else class="grid gap-4">
                <div v-for="dashboard in dashboards" :key="dashboard.id" class="bg-white rounded shadow p-4 flex justify-between items-center">
                    <div>
                        <div class="font-semibold">{{ dashboard.name }}</div>
                        <div class="text-xs text-gray-400">Saved: {{ dashboard.createdAt?.toDate().toLocaleString() }}</div>
                    </div>
                    <div>
                        <button class="btn btn-primary btn-sm" @click="loadDashboard(dashboard)">Load</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { getFirestore, collection, getDocs } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';
import { auth, app } from '@/firebase.js'; 
import { useDataStore } from '@/stores/datasetStore';

export default {
    data() {
        return {
            dashboards: [],
            loading: true,
            user: null
        };
    },
    async mounted() {
        const auth = getAuth(app);
        this.user = auth.currentUser;
        if (!this.user) {
            this.loading = false;
            return;
        }
        const db = getFirestore(app);
        const dashboardsRef = collection(db, 'users', this.user.uid, 'dashboards');
        const snapshot = await getDocs(dashboardsRef);
        this.dashboards = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        this.loading = false;
    },
    methods: {
        loadDashboard(dashboard) {
            const dataStore = useDataStore();
            dataStore.setHeaders(dashboard.headers);
            dataStore.setRows(dashboard.rows);
            localStorage.setItem('dashboardLayout', JSON.stringify(dashboard.widgets));
            this.$router.push({ name: 'DashboardBuilder' });
        }
    }
};
</script>