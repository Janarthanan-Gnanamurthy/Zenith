<template>
	<div class="min-h-screen bg-gray-50">
		<!-- Main Content -->
		<div class="container mx-auto px-4 py-8 sm:px-6 lg:px-8">
			<!-- Loading State -->
			<div v-if="!dataStore.headers.length" class="max-w-md mx-auto text-center">
				<div class="bg-white rounded-xl shadow-md p-8">
					<div class="text-primary mb-4">
						<svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
						</svg>
					</div>
					<h2 class="text-xl font-semibold mb-2">No Data Available</h2>
					<p class="text-gray-600 mb-6">Upload your dataset to start building interactive dashboards.</p>
					<button 
						@click="showFileUploadModal = true" 
						class="btn btn-primary btn-lg w-full"
					>
						Upload CSV Data
					</button>
				</div>
			</div>
			
			<!-- Main Layout -->
			<div v-else>
				<div class="flex justify-between items-center mb-6">
					<div class="flex items-center space-x-3">
						<h1 class="text-3xl font-bold text-gray-900">Dashboard Builder</h1>
						<span class="badge badge-primary">Beta</span>
					</div>
					<div class="flex items-center gap-2">
						<button
							@click="showFileUploadModal = true"
							class="btn btn-outline btn-primary"
						>
							<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-1">
								<path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
							</svg>
							Upload New Data
						</button>
						<!-- <button
							@click="saveDashboardToFirebase"
							class="btn btn-success"
							:disabled="dashboardWidgets.length === 0 || isSaving"
							disabled
						>
							<span v-if="isSaving" class="loading loading-spinner loading-xs mr-2"></span>
							Save Dashboard
						</button> -->
						<DeployDashboard 
							v-if="dashboardWidgets.length > 0" 
							:dashboardWidgets="dashboardWidgets" 
							:datasetInfo="{ headers: dataStore.headers, rows: dataStore.rows }"
						/>
					</div>
				</div>
				
				<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
					<!-- Sidebar -->
					<div class="lg:col-span-1">
						<div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
							<!-- AI Dashboard Generator -->
							<div class="bg-gradient-to-r from-blue-500 to-primary p-5 text-white">
								<h2 class="text-lg font-bold mb-3">AI Dashboard Generator</h2>
								<p class="text-sm opacity-80 mb-4">Describe what insights you want to visualize and our AI will create the perfect dashboard for you.</p>
								<div class="space-y-3">
									<div class="relative">
										<input 
											v-model="dashboardPrompt" 
											class="w-full p-3 pr-12 rounded-lg border-0 bg-white/10 backdrop-blur-sm text-white placeholder-white/60 focus:ring-2 focus:ring-white/50 focus:outline-none"
											placeholder="E.g., Show sales by region and a table of top products"
											@keyup.enter="generateDashboard"
										/>
										<button 
											@click="generateDashboard"
											:disabled="isGenerating || !dashboardPrompt.trim()" 
											class="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
										>
											<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
												<path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
											</svg>
										</button>
									</div>
									<button 
										@click="generateDashboard" 
										class="w-full btn btn-sm md:btn-md" 
										:class="{'btn-outline loading': isGenerating, 'btn-secondary': !isGenerating}"
										:disabled="isGenerating || !dashboardPrompt.trim()"
									>
										{{ isGenerating ? 'Generating...' : 'Generate Dashboard' }}
									</button>
								</div>
							</div>
							
							<!-- Widget Library -->
							<div class="p-5">
								<h3 class="font-medium text-gray-900 mb-4">Add Widgets Manually</h3>
								<div class="grid grid-cols-2 gap-2">
									<button 
										v-for="widget in availableWidgets" 
										:key="widget.type"
										class="flex flex-col items-center justify-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 hover:border-primary transition-all"
										@click="addWidget(widget.type)"
									>
										<svg v-if="widget.type === 'chart'" class="w-8 h-8 text-primary mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 13v-1m4 1v-3m4 3V8M8 21l4-4 4 4M3 4h18M4 4v13a2 2 0 002 2h12a2 2 0 002-2V4"></path>
										</svg>
										
										<svg v-else-if="widget.type === 'table'" class="w-8 h-8 text-primary mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 10h18M3 14h18M3 18h18M3 6h18"></path>
										</svg>
										
										<svg v-else-if="widget.type === 'insight'" class="w-8 h-8 text-primary mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
										</svg>
										
										<svg v-else-if="widget.type === 'stat'" class="w-8 h-8 text-primary mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4v13a2 2 0 002 2h12a2 2 0 002-2V4"></path>
										</svg>
										
										<span class="text-sm font-medium">{{ widget.label }}</span>
									</button>
								</div>
							</div>
						</div>
					</div>

					<!-- Dashboard Canvas -->
					<div class="lg:col-span-3">
						<!-- Empty Dashboard State -->
						<div v-if="!dashboardWidgets.length" class="bg-white rounded-xl border-2 border-dashed border-gray-300 p-10 text-center h-96 flex flex-col items-center justify-center">
							<div class="text-gray-400 mb-4">
								<svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
								</svg>
							</div>
							<h3 class="text-xl font-medium text-gray-500 mb-2">Your dashboard is empty</h3>
							<p class="text-gray-400 mb-6 max-w-md">Add widgets using the tools on the left or use the AI generator to create a complete dashboard in seconds.</p>
							<div class="flex flex-col sm:flex-row gap-3">
								<button 
									@click="addWidget('chart')" 
									class="btn btn-primary"
								>
									<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 13v-1m4 1v-3m4 3V8M8 21l4-4 4 4M3 4h18M4 4v13a2 2 0 002 2h12a2 2 0 002-2V4"></path>
									</svg>
									Add Chart
								</button>
								<button 
									@click="addWidget('table')" 
									class="btn btn-outline"
								>
									<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 10h18M3 14h18M3 18h18M3 6h18"></path>
									</svg>
									Add Table
								</button>
							</div>
						</div>
						
						<!-- Dashboard Grid -->
						<div v-else class="bg-gray-100 rounded-xl p-4 min-h-[600px] dashboard-canvas">
							<div class="grid grid-cols-4 gap-4 auto-rows-min">
								<div
									v-for="widget in dashboardWidgets"
									:key="widget.id"
									class="bg-white rounded-xl shadow-sm relative transition-all duration-200 overflow-hidden"
									:class="[
										getWidgetSizeClass(widget),
										{
											'ring-2 ring-primary ring-offset-2': selectedWidget?.id === widget.id,
											'hover:shadow-md': selectedWidget?.id !== widget.id
										}
									]"
									@click="selectWidget(widget)"
								>
									<!-- Widget Header -->
									<div class="p-3 border-b flex justify-between items-center bg-white">
										<h3 class="font-medium text-gray-700 truncate">{{ widget.config.title }}</h3>
										<div class="flex gap-1">
											<button 
												@click.stop="openWidgetSettings(widget)" 
												class="btn btn-ghost btn-xs btn-square text-gray-500 hover:text-primary"
											>
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
												</svg>
											</button>
											<button 
												@click.stop="removeWidget(widget.id)" 
												class="btn btn-ghost btn-xs btn-square text-gray-500 hover:text-error"
											>
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
												</svg>
											</button>
										</div>
									</div>
									
									<!-- Widget Content -->
									<div class="p-4">
										<component 
											:is="getWidgetComponent(widget)" 
											:widget="widget" 
											:headers="dataStore.headers"
											:rows="dataStore.rows"
											@update:widget="updateWidget"
										/>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Widget Settings Modal -->
		<div 
			v-if="selectedWidget" 
			class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
			@click.self="selectedWidget = null"
		>
			<div class="bg-white rounded-xl shadow-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
				<div class="sticky top-0 bg-white p-4 border-b flex items-center justify-between">
					<h3 class="font-bold text-lg">Widget Settings</h3>
					<button @click="selectedWidget = null" class="btn btn-sm btn-ghost">
						<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>
				
				<div class="p-5 space-y-4">
					<!-- Basic Settings -->
					<div class="form-control">
						<label class="label">
							<span class="label-text">Title</span>
						</label>
						<input 
							v-model="selectedWidget.config.title"
							class="input input-bordered w-full"
							@input="updateWidget(selectedWidget)"
						/>
					</div>

					<!-- Chart Specific Settings -->
					<template v-if="selectedWidget.type === 'chart'">
						<!-- Chart Type -->
						<div class="form-control">
							<label class="label">
								<span class="label-text">Chart Type</span>
							</label>
							<select 
								v-model="selectedWidget.config.chartType"
								class="select select-bordered w-full"
								@input="updateWidget(selectedWidget)"
							>
								<option value="bar">Bar Chart</option>
								<option value="line">Line Chart</option>
								<option value="pie">Pie Chart</option>
								<option value="scatter">Scatter Plot</option>
								<option value="radar">Radar Chart</option>
							</select>
						</div>

						<!-- X-Axis Configuration -->
						<div class="form-control">
							<label class="label">
								<span class="label-text">X-Axis Column</span>
							</label>
							<select 
								v-model="selectedWidget.config.xColumn"
								class="select select-bordered w-full"
								@input="updateWidget(selectedWidget)"
							>
								<option 
									v-for="(header, index) in dataStore.headers" 
									:key="index" 
									:value="index"
								>
									{{ header }}
								</option>
							</select>
						</div>

						<!-- Y-Axis Configuration -->
						<div class="form-control">
							<label class="label">
								<span class="label-text">Y-Axis Columns</span>
								<span class="label-text-alt text-primary">Multiple</span>
							</label>
							<select 
								v-model="selectedWidget.config.yColumns"
								class="select select-bordered w-full" 
								multiple
								size="4"
								@input="updateWidget(selectedWidget)"
							>
								<option 
									v-for="(header, index) in dataStore.headers" 
									:key="index" 
									:value="index"
									:disabled="!isNumericColumn(index)"
									class="py-2"
								>
									{{ header }} {{ !isNumericColumn(index) ? '(non-numeric)' : '' }}
								</option>
							</select>
							<label class="label">
								<span class="label-text-alt">Hold Ctrl/Cmd to select multiple</span>
							</label>
						</div>
					</template>

					<!-- Widget Size Settings -->
					<div class="form-control">
						<label class="label">
							<span class="label-text">Widget Size</span>
						</label>
						<div class="flex flex-wrap gap-2">
							<label 
								v-for="(label, value) in {1: 'Small', 2: 'Medium', 3: 'Large', 4: 'Full'}"
								:key="value"
								class="flex items-center cursor-pointer"
							>
								<input 
									type="radio" 
									:value="value.toString()" 
									v-model="selectedWidget.config.size"
									class="radio radio-sm radio-primary mr-1" 
									@input="updateWidget(selectedWidget)"
								/>
								<span class="text-sm">{{ label }}</span>
							</label>
						</div>
					</div>
					
					<div class="mt-6 flex justify-between">
						<button 
							@click="selectedWidget = null" 
							class="btn btn-ghost"
						>
							Close
						</button>
						<button 
							@click="removeWidget(selectedWidget.id)" 
							class="btn btn-sm btn-error btn-outline"
						>
							Delete Widget
						</button>
					</div>
				</div>
			</div>
		</div>
		
		<!-- File Upload Modal -->
		<div 
			v-if="showFileUploadModal" 
			class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
			@click.self="showFileUploadModal = false"
		>
			<div class="bg-white rounded-xl shadow-lg w-full max-w-xl max-h-[90vh] overflow-y-auto">
				<div class="sticky top-0 bg-gradient-to-r from-indigo-500 to-purple-600 p-6 text-white rounded-t-xl">
					<div class="flex items-center justify-between">
						<h2 class="text-2xl font-bold mb-2 flex items-center gap-2">
							<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
								<path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
							</svg>
							Upload CSV Data
						</h2>
						<button @click="showFileUploadModal = false" class="btn btn-sm btn-circle btn-ghost text-white">
							<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						</button>
					</div>
					<p class="opacity-80">Upload and process your CSV files to create dashboards</p>
				</div>
				
				<div class="p-6">
					<div class="flex flex-col items-center justify-center w-full">
						<label class="flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-xl cursor-pointer border-primary/30 bg-base-200/30 hover:bg-base-200/50 transition-all">
							<div class="flex flex-col items-center justify-center pt-5 pb-6">
								<div class="mb-3 text-primary">
									<svg xmlns="http://www.w3.org/2000/svg" class="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
									</svg>
								</div>
								<p class="mb-2 text-sm font-medium text-gray-700">
									<span class="font-semibold">Click to upload</span> or drag and drop
								</p>
								<p class="text-xs text-gray-500">CSV files only (MAX 10MB)</p>
							</div>
							<input 
								type="file" 
								class="hidden" 
								@change="handleFileUpload" 
								accept=".csv" 
							/>
						</label>
					</div>

					<!-- File Selection Info -->
					<div v-if="uploadedFiles.length > 0" class="mt-6 space-y-3">
						<h3 class="font-medium text-gray-700 flex items-center gap-2">
							<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 text-primary">
								<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
							</svg>
							Selected Files ({{ uploadedFiles.length }})
						</h3>
						
						<div class="divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden">
							<div v-for="(file, index) in uploadedFiles" :key="index" 
								class="flex items-center justify-between p-3 bg-white hover:bg-gray-50">
								<div class="flex items-center gap-3">
									<div class="badge badge-primary">CSV</div>
									<span class="font-medium text-sm">{{ file.name }}</span>
								</div>
								<div class="flex items-center gap-2">
									<span class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</span>
									<button @click="removeFile(index)" class="btn btn-circle btn-ghost btn-xs text-error">
										<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
											<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
										</svg>
									</button>
								</div>
							</div>
						</div>
					</div>
					
					<div class="mt-6 flex justify-end space-x-2">
						<button 
							@click="showFileUploadModal = false" 
							class="btn btn-ghost"
						>
							Cancel
						</button>
						<button 
							@click="processUploadedFiles" 
							class="btn btn-primary"
							:disabled="uploadedFiles.length === 0 || isUploading"
						>
							<span v-if="isUploading" class="loading loading-spinner loading-sm mr-2"></span>
							{{ isUploading ? 'Processing...' : 'Load Data' }}
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { defineComponent } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useDataStore } from '@/stores/datasetStore';
import ChartWidget from './widgets/ChartWidget.vue';
import TableWidget from './widgets/TableWidget.vue';
import InsightWidget from './widgets/InsightWidget.vue';
import StatWidget from './widgets/StatWidget.vue';
import { apiClient } from '@/services/apiService';
import DeployDashboard from './DeployDashboard.vue';
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { getFirestore, collection, addDoc, getDocs, doc, setDoc } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';
import { auth, app } from '@/firebase.js'; // You need to set up this file

export default defineComponent({
	name: 'DashboardBuilder',

	components: {
		ChartWidget,
		TableWidget,
		InsightWidget,
		StatWidget,
		DeployDashboard
	},

	setup() {
		const dataStore = useDataStore();
		const router = useRouter();
		const route = useRoute();
		const debouncedSaveTimeout = ref(null);
		
		const debouncedSave = (fn, delay = 500) => {
			if (debouncedSaveTimeout.value) {
				clearTimeout(debouncedSaveTimeout.value);
			}
			debouncedSaveTimeout.value = setTimeout(() => {
				fn();
			}, delay);
		};
		
		onBeforeUnmount(() => {
			if (debouncedSaveTimeout.value) {
				clearTimeout(debouncedSaveTimeout.value);
			}
		});
		
		return { dataStore, router, route, debouncedSave };
	},

	data() {
		return {
			dashboardWidgets: [],
			selectedWidget: null,
			dashboardPrompt: '',
			isGenerating: false,
			availableWidgets: [
				{ type: 'chart', label: 'Chart Widget' },
				{ type: 'table', label: 'Data Table' },
				{ type: 'insight', label: 'Insight Card' },
				{ type: 'stat', label: 'Statistics' }
			],
			// Store the authentication token in memory to avoid logout
			authToken: localStorage.getItem('authToken') || null,
			showFileUploadModal: false,
			uploadedFiles: [],
			isUploading: false,
			isSaving: false
		};
	},

	created() {
		this.loadDashboard();
		
		// Set up authentication persistence
		if (this.authToken) {
			apiClient.defaults.headers.common['Authorization'] = `Bearer ${this.authToken}`;
		}
		
		// Add event listener for beforeunload to save data
		window.addEventListener('beforeunload', this.handleBeforeUnload);
	},
	
	beforeUnmount() {
		window.removeEventListener('beforeunload', this.handleBeforeUnload);
	},

	methods: {
		isNumericColumn(columnIndex) {
			return this.dataStore.rows.some(row => 
				!isNaN(parseFloat(row[columnIndex])) && row[columnIndex] !== ''
			);
		},

		loadDashboard() {
			// Check if we have data in the store
			if (!this.dataStore.headers.length) {
				return;
			}

			// Load saved dashboard layout
			const savedLayout = localStorage.getItem('dashboardLayout');
			if (savedLayout) {
				try {
					this.dashboardWidgets = JSON.parse(savedLayout);
				} catch (error) {
					console.error('Error loading dashboard layout:', error);
				}
			}
		},

		addWidget(type) {
			// Find first numeric column for Y-axis if it's a chart
			let yColumns = [];
			if (type === 'chart') {
				const firstNumericColumn = this.dataStore.headers.findIndex((_, index) => 
					this.isNumericColumn(index)
				);
				if (firstNumericColumn !== -1) {
					yColumns = [firstNumericColumn];
				}
			}

			const widget = {
				id: `widget-${Date.now()}`,
				type,
				config: {
					title: `New ${type.charAt(0).toUpperCase() + type.slice(1)} Widget`,
					size: '2',
					chartType: type === 'chart' ? 'bar' : null,
					xColumn: 0,
					yColumns: yColumns,
				}
			};
			
			this.dashboardWidgets.push(widget);
			this.saveDashboard();
			this.openWidgetSettings(widget);
		},

		removeWidget(widgetId) {
			this.dashboardWidgets = this.dashboardWidgets.filter(w => w.id !== widgetId);
			if (this.selectedWidget?.id === widgetId) {
				this.selectedWidget = null;
			}
			this.saveDashboard();
		},

		selectWidget(widget) {
			this.selectedWidget = widget;
		},

		openWidgetSettings(widget) {
			this.selectedWidget = widget;
		},

		updateWidget(widget) {
			const index = this.dashboardWidgets.findIndex(w => w.id === widget.id);
			if (index !== -1) {
				// Use Vue's reactivity to update the object in-place
				// to avoid unnecessary re-renders
				Object.assign(this.dashboardWidgets[index], widget);
				
				// Use debounced save for better performance
				this.debouncedSave(() => {
					this.saveDashboard();
				});
			}
		},

		getWidgetComponent(widget) {
			const componentMap = {
				chart: 'ChartWidget',
				table: 'TableWidget',
				insight: 'InsightWidget',
				stat: 'StatWidget'
			};
			return componentMap[widget.type] || 'div';
		},

		getWidgetSizeClass(widget) {
			const sizeMap = {
				'1': 'col-span-1',
				'2': 'col-span-2',
				'3': 'col-span-3',
				'4': 'col-span-4'
			};
			return sizeMap[widget.config.size || '2'];
		},

		saveDashboard() {
			localStorage.setItem('dashboardLayout', JSON.stringify(this.dashboardWidgets));
			// Also preserve auth token to prevent logouts
			if (this.authToken) {
				localStorage.setItem('authToken', this.authToken);
			}
		},

		async generateDashboard() {
			if (!this.dashboardPrompt.trim() || this.isGenerating) return;
			
			this.isGenerating = true;
			try {
				// Convert data to the format expected by the backend
				const columns = this.dataStore.headers;
				const data = this.dataStore.rows.map(row => {
					const rowObj = {};
					row.forEach((value, index) => {
						rowObj[columns[index]] = value;
					});
					return rowObj;
				});
				
				const response = await apiClient.post('http://localhost:8000/api/generate-dashboard', {
					prompt: this.dashboardPrompt,
					columns: columns,
					data: data 
				});
				console.log(response);

				if (response.data && response.data.widgets) {
					// Add all generated widgets
					this.dashboardWidgets = response.data.widgets;
					
					// Save to localStorage
					this.saveDashboard();
					
					// Clear prompt
					this.dashboardPrompt = '';
				}
			} catch (error) {
				console.error('Error generating dashboard:', error);
				alert('Failed to generate dashboard. Please try again with a different prompt.');
			} finally {
				this.isGenerating = false;
			}
		},

		handleFileUpload(event) {
			const files = Array.from(event.target.files);
			if (files.length > 0) {
				this.uploadedFiles = files;
			}
		},

		removeFile(index) {
			this.uploadedFiles.splice(index, 1);
		},
		
		formatFileSize(bytes) {
			if (bytes === 0) return '0 Bytes';
			
			const k = 1024;
			const sizes = ['Bytes', 'KB', 'MB', 'GB'];
			const i = Math.floor(Math.log(bytes) / Math.log(k));
			
			return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
		},

		async processUploadedFiles() {
			if (!this.uploadedFiles.length) return;
			
			this.isUploading = true;
			
			try {
				// Clear any existing data in the store
				this.dataStore.clearData();
				
				// Clear all existing dashboard widgets since we're loading a new dataset
				this.dashboardWidgets = [];
				
				// Process the first file (for now, we'll just support one file)
				const file = this.uploadedFiles[0];
				const text = await file.text();
				const lines = text.trim().split('\n');
				const headers = lines[0].split(',').map(header => header.trim());
				
				const rows = [];
				for (let i = 1; i < lines.length; i++) {
					if (lines[i].trim()) {
						const values = lines[i].split(',').map(value => value.trim());
						rows.push(values);
					}
				}
				
				// Store the data in the data store
				this.dataStore.setHeaders(headers);
				this.dataStore.setRows(rows);
				
				// Save the empty dashboard layout
				this.saveDashboard();
				
				// Close the modal
				this.showFileUploadModal = false;
				
				// Clear uploaded files
				this.uploadedFiles = [];
				
			} catch (error) {
				console.error('Error processing file:', error);
				alert('Error processing file. Please try again with a different file.');
			} finally {
				this.isUploading = false;
			}
		},

		// Force save on page unload
		handleBeforeUnload() {
			this.saveDashboard();
		},

		async saveDashboardToFirebase() {
			this.isSaving = true;
			try {
				const auth = getAuth(app);
				const user = auth.currentUser;
				if (!user) {
					alert('You must be logged in to save dashboards.');
					this.isSaving = false;
					return;
				}
				const db = getFirestore(app);
				const dashboardsRef = collection(db, 'users', user.uid, 'dashboards');

				// Convert rows (array of arrays) to array of objects
				const headers = this.dataStore.headers;
				const rows = this.dataStore.rows.map(rowArr => {
					const rowObj = {};
					headers.forEach((header, idx) => {
						rowObj[header] = rowArr[idx];
					});
					return rowObj;
				});

				const cleanWidgets = JSON.parse(JSON.stringify(this.dashboardWidgets, (key, value) => {
					// Remove undefined/null
					if (value === undefined || value === null) return undefined;
					// Prevent nested arrays
					if (Array.isArray(value)) {
						return value.filter(v => v !== undefined && v !== null && !Array.isArray(v));
					}
					return value;
				}));

				const dashboardData = {
					widgets: cleanWidgets,
					headers: headers,
					rows: rows,
					createdAt: new Date(),
					name: cleanWidgets[0]?.config?.title || 'Untitled Dashboard'
				};
				await addDoc(dashboardsRef, dashboardData);
				alert('Dashboard saved!');
			} catch (e) {
				console.error(e);
				alert('Failed to save dashboard.');
			}
			this.isSaving = false;
		}
	}
});
</script>

<style>
.dashboard-widget-enter-active,
.dashboard-widget-leave-active {
  transition: all 0.3s ease;
}

.dashboard-widget-enter-from,
.dashboard-widget-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Custom card style for widgets */
.bg-white.rounded-xl {
  transition: all 0.2s ease-in-out;
}

/* Better focus styles for inputs */
.input:focus, .select:focus {
  border-color: #000;
  box-shadow: 0 0 0 2px rgba(var(--p), 0.2);
}

/* Nice hover effect for widget cards */
.dashboard-canvas .bg-white.rounded-xl:hover:not(.ring-2) {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* Smooth transition for sidebar elements */
.form-control, .btn, .select, .input {
  transition: all 0.2s ease;
}

/* Better scrollbar for multi-select */
select[multiple] {
  scrollbar-width: thin;
  scrollbar-color: rgba(var(--p), 0.5) rgba(var(--b2), 0.2);
}

select[multiple]::-webkit-scrollbar {
  width: 8px;
}

select[multiple]::-webkit-scrollbar-track {
  background: rgba(var(--b2), 0.2);
  border-radius: 4px;
}

select[multiple]::-webkit-scrollbar-thumb {
  background-color: rgba(var(--p), 0.5);
  border-radius: 4px;
}
</style>