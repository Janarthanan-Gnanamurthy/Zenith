<template>
  <div class="deploy-dashboard">
    <button 
      @click="openDeployModal" 
      :class="['btn', isDeploying ? 'btn-primary loading' : 'btn-primary', $attrs.class]"
      :disabled="isDeploying"
    >
      <span v-if="!isDeploying" class="flex items-center">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"></path>
        </svg>
        Share Dashboard
      </span>
      <span v-else>Sharing...</span>
    </button>

    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-bold mb-4">Share Your Dashboard</h3>
        
        <div v-if="deploymentStage === 'initial'">
          <p class="mb-4">Create a public link to share your dashboard with others.</p>
          <div class="mb-4">
            <label class="block text-sm font-medium mb-1">Dashboard Name</label>
            <input 
              v-model="dashboardName" 
              class="input input-bordered w-full"
              placeholder="My Awesome Dashboard"
            />
          </div>
          <div class="flex justify-end gap-2">
            <button @click="closeModal" class="btn btn-ghost">Cancel</button>
            <button @click="deployDashboard" class="btn btn-primary">Deploy</button>
          </div>
        </div>

        <div v-else-if="deploymentStage === 'deploying'" class="text-center py-6">
          <div class="loading loading-spinner loading-lg text-primary mx-auto"></div>
          <p class="mt-4 text-lg">Setting up your dashboard...</p>
          <p class="text-sm text-gray-500 mt-2">This may take a moment.</p>
        </div>

        <div v-else-if="deploymentStage === 'success'" class="py-4">
          <div class="flex items-center justify-center mb-4">
            <svg class="w-10 h-10 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h4 class="text-lg font-semibold text-center mb-4">Dashboard Published!</h4>
          
          <div class="bg-gray-50 p-3 rounded mb-4">
            <label class="block text-sm font-medium mb-1">Share this link:</label>
            <div class="join w-full">
              <input 
                ref="shareUrlInput"
                readonly
                :value="deployedUrl" 
                class="input join-item input-bordered w-full bg-white"
              />
              <button 
                @click="copyShareUrl" 
                class="btn join-item"
                :class="copied ? 'btn-success' : 'btn-neutral'"
              >
                <svg v-if="!copied" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path>
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </button>
            </div>
          </div>
          
          <div class="flex justify-end">
            <button @click="closeModal" class="btn btn-primary">Done</button>
          </div>
        </div>

        <div v-else-if="deploymentStage === 'error'" class="py-4">
          <div class="flex items-center justify-center mb-4">
            <svg class="w-10 h-10 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
          <h4 class="text-lg font-semibold text-center mb-2">Deployment Failed</h4>
          <p class="text-center text-gray-600 mb-4">{{ errorMessage }}</p>
          
          <div class="flex justify-end">
            <button @click="closeModal" class="btn btn-ghost mr-2">Close</button>
            <button @click="resetDeployment" class="btn btn-primary">Try Again</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { apiClient } from '@/services/apiService';

export default defineComponent({
  name: 'DeployDashboard',
  
  props: {
    dashboardWidgets: {
      type: Array,
      required: true
    },
    datasetInfo: {
      type: Object,
      required: true
    }
  },
  
  data() {
    return {
      showModal: false,
      isDeploying: false,
      deploymentStage: 'initial', // 'initial', 'deploying', 'success', 'error'
      dashboardName: '',
      deployedUrl: '',
      errorMessage: '',
      copied: false
    };
  },

  inheritAttrs: false,
  
  methods: {
    openDeployModal() {
      this.showModal = true;
      this.deploymentStage = 'initial';
      // Pre-populate with a default dashboard name
      this.dashboardName = `Dashboard ${new Date().toLocaleDateString()}`;
    },
    
    closeModal() {
      this.showModal = false;
    },
    
    resetDeployment() {
      this.deploymentStage = 'initial';
    },
    
    async deployDashboard() {
      if (!this.dashboardName.trim()) {
        this.errorMessage = 'Please enter a dashboard name';
        this.deploymentStage = 'error';
        return;
      }
      
      // Check if dataset has data
      const hasData = this.datasetInfo && 
                      this.datasetInfo.headers && 
                      this.datasetInfo.headers.length > 0 && 
                      this.datasetInfo.rows && 
                      this.datasetInfo.rows.length > 0;
      
      if (!hasData) {
        if (!confirm('This dashboard appears to have no data. Widgets will appear empty in the shared view. Continue anyway?')) {
          return;
        }
      }
      
      this.deploymentStage = 'deploying';
      this.isDeploying = true;
      
      try {
        // Prepare dashboard data
        const dashboardData = {
          name: this.dashboardName.trim(),
          widgets: this.dashboardWidgets,
          dataset: {
            headers: this.datasetInfo.headers,
            rows: this.datasetInfo.rows
          }
        };
        
        // Deploy dashboard using authenticated API client
        const response = await apiClient.post('/api/deploy-dashboard', dashboardData);
        
        const data = response.data;
        
        // Set the deployed URL
        this.deployedUrl = data.deployUrl;
        this.deploymentStage = 'success';
      } catch (error) {
        console.error('Error deploying dashboard:', error);
        this.errorMessage = 'Failed to deploy dashboard. Please try again.';
        this.deploymentStage = 'error';
      } finally {
        this.isDeploying = false;
      }
    },
    
    copyShareUrl() {
      navigator.clipboard.writeText(this.deployedUrl)
        .then(() => {
          this.copied = true;
          setTimeout(() => {
            this.copied = false;
          }, 2000);
        })
        .catch(err => {
          console.error('Failed to copy URL: ', err);
        });
    }
  }
});
</script>

<style scoped>
.deploy-dashboard {
  display: inline-block;
}

/* Ensure the button maintains consistent width */
.btn {
  min-width: 140px;
}
</style> 