<template>
	<div class="flex flex-col relative h-screen">
		<!-- Page Content -->
		<main class="flex-1 overflow-y-auto">
			<div class="container mx-auto px-4 py-8">
				<!-- Page Header -->
				<div class="mb-10 text-center">
					<h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600 mb-4">
						Intelligent Data Analysis Suite
					</h1>
					<p class="text-lg text-gray-600 max-w-2xl mx-auto">
						Transform raw data into actionable insights with our AI-powered platform
					</p>
				</div>
				
				<!-- Main Content Area with Vertical Layout -->
				<div class="flex flex-col gap-8">
					<!-- Upload Widget -->
					<div class="w-full">
						<div class="card bg-base-100 shadow-xl overflow-hidden border border-gray-100 mb-6">
							<div class="card-body p-0">
								<div class="bg-gradient-to-r from-indigo-500 to-purple-600 p-6 text-white">
									<div class="flex items-center gap-2 mb-1">
										<h2 class="card-title text-2xl flex items-center gap-2">
											<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
												<path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
											</svg>
											Data Source
										</h2>
										<span class="badge badge-sm bg-white/20 border-none">Multiple Files Supported</span>
									</div>
									<p class="opacity-80">Upload and process your CSV files for analysis</p>
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
												<p class="text-xs text-primary mt-1">Files are added automatically. Hold Ctrl to replace all files.</p>
											</div>
											<input 
												type="file" 
												class="hidden" 
												@change="handleFileUpload" 
												accept=".csv" 
												multiple
											/>
										</label>
									</div>

									<!-- File Selection Info -->
									<div v-if="files.length > 0" class="mt-6">
										<h3 class="font-medium text-gray-700 flex items-center gap-2 mb-3">
											<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 text-primary">
												<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
											</svg>
											Selected Files ({{ files.length }})
										</h3>
										
										<div class="divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden max-h-60 overflow-y-auto">
											<div v-for="(file, index) in files" :key="index" 
												class="flex items-center justify-between p-3 bg-white hover:bg-gray-50">
												<div class="flex items-center gap-3 overflow-hidden">
													<div class="badge badge-primary shrink-0">CSV</div>
													<span class="font-medium text-sm truncate">{{ file.name }}</span>
												</div>
												<div class="flex items-center gap-2 shrink-0">
													<span class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</span>
													<button @click="removeFile(index)" class="btn btn-circle btn-ghost btn-xs text-error">
														<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
															<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
														</svg>
													</button>
												</div>
											</div>
										</div>

										<div class="mt-3 text-xs text-gray-500">
											<span v-if="files.length > 5">Scroll to see all files</span>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
					
					<!-- Data Preview Section - Now Below Upload -->
					<div v-if="previewData.length > 0" class="w-full">
						<div class="card bg-base-100 shadow-xl border border-gray-100 mb-8">
							<div class="card-body p-0">
								<div class="bg-gradient-to-r from-teal-500 to-emerald-500 p-6 text-white">
									<h2 class="card-title text-2xl mb-2 flex items-center gap-2">
										<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
											<path stroke-linecap="round" stroke-linejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0112 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M3.375 8.25c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m17.25-3.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5M12 10.875v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125M13.125 12h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125M20.625 12c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5M12 14.625v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 14.625c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m0 1.5v-1.5m0 0c0-.621.504-1.125 1.125-1.125m0 0h7.5" />
									</svg>
									Data Preview
								</h2>
								<p class="opacity-80">Sample of your uploaded data</p>
							</div>
							
							<div class="p-6 space-y-6">
								<!-- File tabs with scroll for many files -->
								<div class="relative">
									<div class="overflow-x-auto pb-1">
										<div class="tabs tabs-boxed inline-flex whitespace-nowrap min-w-full">
											<a v-for="(fileData, index) in previewData" 
												:key="index" 
												:class="['tab', {'tab-active': activePreviewTab === index}]"
												@click="activePreviewTab = index">
												{{ files[index] && files[index].name ? 
													(files[index].name.length > 15 ? files[index].name.substring(0, 15) + '...' : files[index].name) : 
													'File ' + (index + 1) }}
											</a>
										</div>
									</div>
									<div v-if="previewData.length > 3" class="absolute right-0 top-0 text-xs text-gray-500 mb-1">
										← Scroll to see all files →
									</div>
								</div>
								
								<div v-for="(fileData, index) in previewData" 
									:key="index" 
									:class="{'hidden': activePreviewTab !== index}">
									<div class="overflow-x-auto border rounded-lg">
										<table class="table table-zebra w-full">
											<thead>
												<tr>
													<th v-for="header in fileData.headers" :key="header" 
														class="bg-base-200 text-xs font-medium uppercase">
														{{ header }}
													</th>
												</tr>
											</thead>
											<tbody>
												<tr v-for="(row, rowIndex) in fileData.displayedRows" :key="rowIndex">
													<td v-for="(cell, cellIndex) in row" :key="cellIndex" 
														class="text-sm">
														{{ cell }}
													</td>
												</tr>
											</tbody>
										</table>
									</div>
									<div class="mt-3 flex justify-between items-center">
										<span class="text-sm text-gray-600">File: <span class="font-medium">{{ files[index].name }}</span></span>
										<span class="badge badge-neutral">
											Showing {{ fileData.displayedRows.length }} of {{ fileData.totalRows }} rows
										</span>
									</div>
								</div>
							</div>
						</div>
					</div>
					
					<!-- Processing Results -->
					<div v-if="processedData" class="w-full">
						<div class="card bg-base-100 shadow-xl border border-gray-100">
							<div class="card-body p-0">
								<div class="bg-gradient-to-r from-amber-500 to-orange-500 p-6 text-white">
									<h2 class="card-title text-2xl mb-2 flex items-center gap-2">
										<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
											<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
										</svg>
										Analysis Results
									</h2>
									<p class="opacity-80">Insights from your data</p>
								</div>
								<!-- Chart Result -->
								<div v-if="processedData.type === 'chart'" class="p-6">
									<div class="bg-base-200/50 rounded-xl p-6 mb-6">
										<h3 class="text-lg font-medium mb-4 text-base-content">{{ processedData.config?.options?.plugins?.title?.text || 'Visualization' }}</h3>
										<div class="chart-container aspect-[4/3] max-h-[500px]">
											<canvas ref="chartCanvas"></canvas>
										</div>
									</div>
									<div class="flex justify-end gap-3">
										<button @click="saveToCollection" class="btn btn-outline">
											<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-1">
												<path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" />
											</svg>
											Save Chart
										</button>
										<button @click="downloadChartImage" class="btn btn-primary">
											<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-1">
												<path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
											</svg>
											Download
										</button>
									</div>
								</div>
								<!-- Table Result -->
								<div v-else-if="processedData.type === 'table'" class="p-6">
									<div class="bg-base-200/50 rounded-xl p-6 mb-6">
										<h3 class="text-lg font-medium mb-4 text-base-content">Transformed Data</h3>
										<div v-if="processedData.data && processedData.data.length > 0" class="overflow-x-auto">
											<table class="table w-full">
												<thead>
													<tr>
														<th v-for="column in Object.keys(processedData.data[0] || {})" :key="column" class="bg-base-200 text-xs font-medium uppercase">
															{{ column }}
														</th>
													</tr>
												</thead>
												<tbody>
													<tr v-for="(row, rowIndex) in processedData.data.slice(0, 20)" :key="rowIndex">
														<td v-for="(value, column) in row" :key="column" class="text-sm whitespace-nowrap">
															{{ value }}
														</td>
													</tr>
												</tbody>
											</table>
											<div v-if="processedData.data.length > 20" class="mt-3 text-center text-sm text-gray-600">
												Showing first 20 rows of {{ processedData.data.length }} total rows
											</div>
										</div>
										<div v-else class="text-center py-8 text-gray-500">
											<p>No data available to display</p>
											<p class="text-sm mt-2">{{ processedData.message || 'Transformation completed but no data was returned.' }}</p>
										</div>
									</div>
									<div class="flex justify-end">
										<button @click="downloadData" class="btn btn-primary" :disabled="!processedData.data || processedData.data.length === 0">
											<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-1">
												<path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
											</svg>
											Download CSV
										</button>
									</div>
								</div>
								<!-- Statistical Result -->
								<div v-else-if="processedData.type === 'statistical_result'" class="p-6">
									<div class="bg-base-200/50 rounded-xl p-6 mb-6">
										<h3 class="text-lg font-medium mb-4 text-base-content">Statistical Analysis</h3>
										<div v-if="Array.isArray(processedData.result) && processedData.result.length && typeof processedData.result[0] === 'object'">
											<table class="table w-full">
												<thead>
													<tr>
														<th v-for="column in Object.keys(processedData.result[0] || {})" :key="column" class="bg-base-200 text-xs font-medium uppercase">
															{{ column }}
														</th>
													</tr>
												</thead>
												<tbody>
													<tr v-for="(row, rowIndex) in processedData.result" :key="rowIndex">
														<td v-for="(value, column) in row" :key="column" class="text-sm whitespace-nowrap">
															{{ value }}
														</td>
													</tr>
												</tbody>
											</table>
										</div>
										<div v-else-if="typeof processedData.result === 'object' && processedData.result !== null">
											<pre class="bg-base-200 rounded p-4 text-xs overflow-x-auto">{{ JSON.stringify(processedData.result, null, 2) }}</pre>
										</div>
										<div v-else>
											<p class="text-base-content">{{ processedData.result }}</p>
										</div>
									</div>
									<div class="flex justify-end">
										<button @click="downloadStatisticalData" class="btn btn-primary">
											<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-1">
												<path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
											</svg>
											Download CSV
										</button>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
			</div>
		</main>
		
		<!-- Sticky Text Prompt at Bottom -->
		<div class="sticky bottom-0 left-0 right-0 z-10 bg-base-100 border-t border-gray-200 shadow-lg">
			<div class="container mx-auto p-4">
				<div class="card bg-base-100">
					<div class="card-body p-4">
						<h2 class="card-title text-xl mb-3 flex items-center gap-2">
							<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 text-primary">
								<path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
							</svg>
							AI Analysis
						</h2>
						
						<div class="flex items-center gap-3">
							<textarea 
								v-model="userPrompt" 
								class="textarea textarea-bordered flex-1" 
								placeholder="e.g., 'Show me a bar chart of sales by region' or 'Calculate the average revenue'"
							></textarea>
							
							<button 
								@click="processData" 
								class="btn btn-primary"
								:disabled="files.length === 0 || !userPrompt || loading"
							>
								<svg v-if="!loading" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
								</svg>
								<span v-if="loading" class="loading loading-spinner loading-sm"></span>
								{{ loading ? 'Processing...' : 'Analyze' }}
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
		
		<!-- Loading Overlay -->
		<div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
			<div class="card bg-base-100 p-8 shadow-2xl max-w-md">
				<div class="flex justify-center mb-4">
					<div class="loading loading-spinner loading-lg text-primary"></div>
				</div>
				<h3 class="text-xl font-bold text-center mb-2">Processing Your Request</h3>
				<p class="text-center text-base-content/70">Our AI is analyzing your data and generating insights...</p>
			</div>
		</div>
	</div>
</template>


<script>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Chart from 'chart.js/auto';
import * as XLSX from 'xlsx';
import { useDataStore } from '@/stores/datasetStore';
import NavBar from './NavBar.vue';

export default {
	name: 'DataProcessor',
	components: {
		NavBar
	},
	
	setup() {
		const router = useRouter();
		const dataStore = useDataStore();
		const files = ref([]);
		const previewData = ref([]);
		const userPrompt = ref('');
		const processedData = ref(null);
		const loading = ref(false);
		const chartCanvas = ref(null);
		const chartInstance = ref(null);
		const activePreviewTab = ref(0);
		const headers = ref([]);
		const rows = ref([]);
		
		axios.defaults.baseURL = 'https://test.edventuretech.in/';
		
		// Handle file upload
		const handleFileUpload = (event) => {
			// Convert FileList to Array to ensure all files are processed
			const newFiles = Array.from(event.target.files || []);
			
			// Validate file types
			const invalidFiles = newFiles.filter(file => !file.name.toLowerCase().endsWith('.csv'));
			if (invalidFiles.length > 0) {
				alert('Only CSV files are supported');
				return;
			}
			
			if (newFiles.length > 0) {
				// Show loading spinner for preview generation
				loading.value = true;
				
				// By default, append files instead of replacing them
				// Only replace if Ctrl key is pressed during upload
				if (event.ctrlKey) {
					// If Ctrl key is pressed, replace existing files
					files.value = newFiles;
					previewData.value = [];
					activePreviewTab.value = 0;
				} else {
					// Otherwise append to existing files (default behavior)
					files.value = [...files.value, ...newFiles];
				}
				
				loadPreviewData(newFiles);
			}
		};
		
		// Load preview data from files
		const loadPreviewData = (newFiles) => {
			newFiles.forEach(file => {
				const reader = new FileReader();
				reader.onload = (e) => {
					const content = e.target.result;
					const lines = content.split('\n');
					const fileHeaders = lines[0].split(',');
					const fileRows = lines.slice(1)
						.filter(line => line.trim())
						.map(line => line.split(','));
					
					headers.value = fileHeaders;
					rows.value = fileRows;
					
					previewData.value.push({
						headers: fileHeaders,
						displayedRows: fileRows.slice(0, 5),
						totalRows: fileRows.length
					});
					
					// If this is the first file being added, set it as active tab
					if (previewData.value.length === 1) {
						activePreviewTab.value = 0;
					}
					
					loading.value = false;
				};
				reader.readAsText(file);
			});
		};
		
		// Process a single file to generate preview (from original)
		const processFilePreview = async (file) => {
			try {
				const text = await file.text();
				const lines = text.trim().split('\n');
				const fileHeaders = lines[0].split(',').map(header => header.trim());
				
				const fileRows = [];
				for (let i = 1; i < Math.min(lines.length, 6); i++) {
					const values = lines[i].split(',').map(value => value.trim());
					fileRows.push(values);
				}
				
				previewData.value.push({
					headers: fileHeaders,
					displayedRows: fileRows,
					totalRows: lines.length - 1
				});
				
				// If this is the first file being added, set it as active tab
				if (previewData.value.length === 1) {
					activePreviewTab.value = 0;
				}
			} catch (error) {
				console.error(`Error parsing CSV file '${file.name}':`, error);
			}
		};
		
		// Remove a file from the list
		const removeFile = (index) => {
			// Remove the file from the files array
			files.value.splice(index, 1);
			
			// Remove corresponding preview data
			previewData.value.splice(index, 1);
			
			// Adjust activePreviewTab if needed
			if (previewData.value.length === 0) {
				// No files left, reset everything
				activePreviewTab.value = 0;
				headers.value = [];
				rows.value = [];
			} else if (activePreviewTab.value >= previewData.value.length) {
				// If we were viewing a tab that no longer exists, go to the last available tab
				activePreviewTab.value = previewData.value.length - 1;
			}
			// Otherwise, keep the current active tab

			// Show notification if all files are removed
			if (files.value.length === 0) {
				// This would be where you'd show a notification
				console.log('All files removed');
			}
		};
		
		// Format file size for display
		const formatFileSize = (bytes) => {
			if (bytes === 0) return '0 Bytes';
			
			const k = 1024;
			const sizes = ['Bytes', 'KB', 'MB', 'GB'];
			const i = Math.floor(Math.log(bytes) / Math.log(k));
			
			return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
		};
		
		// Process data based on user prompt
		const processData = async () => {
			if (files.value.length === 0 || !userPrompt.value) {
				alert('Please upload files and enter a prompt.');
				return;
			}

			loading.value = true;
			processedData.value = null;

			try {
				console.log('Processing data with prompt:', userPrompt.value);
				
				const formData = new FormData();
				
				// Check if we're using real files or transformed data
				const isRealFiles = files.value.some(file => file.size > 0);
				
				if (isRealFiles) {
					// Important change: Use the same field name "files" for all files
					// This matches the FastAPI endpoint expectation: List[UploadFile] = File(...)
					files.value.forEach(file => {
						formData.append('files', file);
					});
				} else {
					// We're working with transformed data
					console.log('Using transformed data from previous operations');
					
					// Create a CSV representation of our data
					const csvContent = [
						headers.value.join(','),
						...rows.value.map(row => 
							headers.value.map(header => 
								typeof row[header] === 'undefined' ? '' : row[header]
							).join(',')
						)
					].join('\n');
					
					// Create a file from the CSV content and append with the correct field name
					const transformedFile = new File([csvContent], 'transformed_data.csv', { type: 'text/csv' });
					formData.append('files', transformedFile);
					console.log('Created transformed file:', transformedFile);
				}
				
				// Add the prompt as a form field
				formData.append('prompt', userPrompt.value);

				const response = await axios.post('/api/process', formData, {
					headers: {
						'Content-Type': 'multipart/form-data'
					}
				});
				
				console.log('Received data from backend:', response.data);
				processedData.value = response.data;
				
				// If visualization type, create chart
				if (processedData.value.type === 'chart') {
					console.log('Chart data:', processedData.value.config);
					await nextTick();
					updateChart();
				}
			} catch (error) {
				console.error('Error processing data:', error);
				alert('An error occurred while processing your request. Please try again.');
			} finally {
				loading.value = false;
			}
		};
		
		// Navigate to dashboard builder
		const goToDashboard = () => {
			if (!files.value.length) {
				alert('Please upload a file first.');
				return;
			}

			try {
				// Store the data directly in the store state
				dataStore.$state.files = files.value;
				dataStore.$state.previewData = previewData.value;
				dataStore.$state.headers = headers.value;
				dataStore.$state.rows = rows.value;
				
				// Save to sessionStorage manually
				sessionStorage.setItem('dataStore', JSON.stringify({
					files: files.value,
					previewData: previewData.value,
					headers: headers.value,
					rows: rows.value,
					processedData: null
				}));
				
				console.log('Data stored for dashboard builder');
				
				// Navigate to dashboard builder
				router.push({ name: 'DashboardBuilder' });
			} catch (error) {
				console.error('Error in goToDashboard:', error);
				alert('An error occurred while preparing the dashboard. Please try again.');
			}
		};
		
		// Update chart visualization
		const updateChart = async () => {
			if (chartInstance.value) {
				chartInstance.value.destroy();
			}

			try {
				if (!chartCanvas.value) {
					console.error('Chart canvas element not found');
					return;
				}

				const ctx = chartCanvas.value.getContext('2d');
				if (!ctx) {
					console.error('Chart canvas context not found');
					return;
				}

				const chartConfig = processedData.value?.config;
				console.log('Chart data before creation:', chartConfig);
				
				if (!chartConfig) {
					console.error('No visualization data available');
					return;
				}

				// Wait for the next tick to ensure canvas is ready
				await nextTick();

				// Ensure proper canvas dimensions
				chartCanvas.value.style.height = '400px';
				chartCanvas.value.style.width = '100%';

				// Create chart configuration
				const chartInstance = new Chart(ctx, chartConfig);

			} catch (error) {
				console.error('Error creating chart:', error);
				console.error('Error details:', error.message);
			}
		};
		
		// Format currency values
		const formatCurrency = (value) => {
			return new Intl.NumberFormat('en-IN', {
				style: 'currency',
				currency: 'INR',
				maximumFractionDigits: 0,
			}).format(value);
		};
		
		// Create chart visualization (original function)
		const createChart = () => {
			if (chartInstance.value) {
				chartInstance.value.destroy();
			}
			
			if (!chartCanvas.value) {
				return;
			}

			const ctx = chartCanvas.value.getContext('2d');
			
			chartInstance.value = new Chart(ctx, {
				type: processedData.value.chartType || 'bar',
				data: processedData.value.chartData,
				options: processedData.value.chartOptions || {
					responsive: true,
					maintainAspectRatio: false,
					plugins: {
						legend: {
							position: 'top',
						},
						title: {
							display: true,
							text: processedData.value.title || 'Data Visualization'
						}
					}
				}
			});
		};
		
		// Download chart as image
		const downloadChartImage = () => {
			if (!chartCanvas.value) {
				console.error('Chart instance not found');
				return;
			}
			
			try {
				// Convert canvas to image
				const image = chartCanvas.value.toDataURL('image/png', 1.0);
				
				// Create download link
				const link = document.createElement('a');
				link.download = 'chart.png';
				link.href = image;
				link.click();
			} catch (error) {
				console.error('Error downloading chart image:', error);
				alert('An error occurred while downloading the chart. Please try again.');
			}
		};
		
		// Download processed data
		const downloadData = () => {
			if (!processedData.value) return;
			
			if (processedData.value.type === 'chart') {
				downloadChartImage();
				return;
			}
			
			let dataToDownload;
			let filename = 'transformed_data.csv';

			if (processedData.value.type === 'table') {
				// For table data - ensure we have valid data
				if (!processedData.value.data || !Array.isArray(processedData.value.data) || processedData.value.data.length === 0) {
					console.error('No valid data to download');
					alert('No data available to download');
					return;
				}
				dataToDownload = processedData.value.data;
				filename = 'transformed_data.csv';
			} else if (processedData.value.type === 'statistical_result') {
				// For statistical data - ensure we have valid data
				if (!processedData.value.result) {
					console.error('No statistical result to download');
					alert('No statistical data available to download');
					return;
				}
				
				// Handle different result formats
				if (Array.isArray(processedData.value.result)) {
					dataToDownload = processedData.value.result;
				} else if (typeof processedData.value.result === 'object') {
					// Convert object to array format
					dataToDownload = [processedData.value.result];
				} else {
					console.error('Unexpected statistical result format');
					alert('Statistical data format not supported for download');
					return;
				}
				filename = 'statistical_analysis.csv';
			} else {
				console.error('Unknown data type for download');
				alert('Unknown data type for download');
				return;
			}

			try {
				// Ensure we have at least one row with data
				if (!dataToDownload || dataToDownload.length === 0) {
					console.error('No data rows to download');
					alert('No data available to download');
					return;
				}

				// Get headers from the first row
				const headers = Object.keys(dataToDownload[0]);
				if (headers.length === 0) {
					console.error('No headers found in data');
					alert('No valid data structure for download');
					return;
				}

				// Convert data to CSV format
				const csvContent = [
					headers.join(','),
					...dataToDownload.map(row => 
						headers.map(header => {
							const value = row[header];
							// Handle different data types and escape commas
							if (value === null || value === undefined) {
								return '';
							}
							const stringValue = String(value);
							// Escape quotes and wrap in quotes if contains comma
							if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
								return `"${stringValue.replace(/"/g, '""')}"`;
							}
							return stringValue;
						}).join(',')
					)
				].join('\n');

				// Create and trigger download
				const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
				const link = document.createElement('a');
				const url = URL.createObjectURL(blob);
				link.setAttribute('href', url);
				link.setAttribute('download', filename);
				link.style.visibility = 'hidden';
				document.body.appendChild(link);
				link.click();
				document.body.removeChild(link);
				URL.revokeObjectURL(url);
			} catch (error) {
				console.error('Error downloading data:', error);
				alert('An error occurred while downloading the data. Please try again.');
			}
		};
		
		// Download statistical data as CSV (original function)
		const downloadStatisticalData = () => {
			if (!processedData.value || !processedData.value.result || processedData.value.result.length === 0) {
				return;
			}
			
			const headers = Object.keys(processedData.value.result[0]);
			let csvContent = headers.join(',') + '\n';
			
			processedData.value.result.forEach(row => {
				const rowData = headers.map(header => row[header]);
				csvContent += rowData.join(',') + '\n';
			});
			
			const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
			const link = document.createElement('a');
			link.href = URL.createObjectURL(blob);
			link.download = 'data_analysis.csv';
			link.click();
		};
		
		// Continue with further data modifications
		const continueModification = () => {
			console.log('Continue Modification clicked', processedData.value);
			
			try {
				// Store the processed data in the store
				dataStore.$state.processedData = processedData.value;
				console.log('Data stored directly in Pinia store state');
				
				// Clear the current prompt to allow for new modifications
				userPrompt.value = '';
				
				// Handle different data types
				if (processedData.value.type === 'chart') {
					// For visualization, extract the data from the chart
					const datasets = processedData.value.config.data.datasets;
					const labels = processedData.value.config.data.labels;
					
					console.log('Visualization data before conversion:', datasets, labels);
					
					// Create a format that can be displayed in the preview table
					const data = labels.map((label, index) => {
						const row = { Category: label };
						datasets.forEach((dataset, datasetIndex) => {
							row[dataset.label || `Series ${datasetIndex + 1}`] = dataset.data[index];
						});
						return row;
					});
					
					const columns = ['Category', ...datasets.map((d, i) => d.label || `Series ${i + 1}`)];
					
					console.log('Converted visualization data:', data);
					console.log('Columns:', columns);
					
					// Create a single new file representation
					files.value = [new File([], 'visualization_data.csv')];
					
					// Update preview data - replace all existing preview data
					previewData.value = [{
						headers: columns,
						displayedRows: data.slice(0, 5),
						totalRows: data.length
					}];
					
					headers.value = columns;
					rows.value = data;
					
					console.log('Updated preview data for visualization', previewData.value);
				} 
				else if (processedData.value.type === 'statistical_result') {
					// For statistical data
					let resultData = processedData.value.result;
					
					// Handle different result formats
					if (Array.isArray(resultData)) {
						// Already in array format
					} else if (typeof resultData === 'object' && resultData !== null) {
						// Convert object to array format
						resultData = [resultData];
					} else {
						console.error('Unexpected statistical result format');
						alert('Statistical data format not supported for continued modification');
						return;
					}
					
					if (resultData.length === 0) {
						console.error('No statistical data available');
						alert('No statistical data available for continued modification');
						return;
					}
					
					const columns = Object.keys(resultData[0] || {});
					
					console.log('Statistical data before conversion:', resultData);
					console.log('Columns:', columns);
					
					// Create a single new file representation
					files.value = [new File([], 'statistical_data.csv')];
					
					// Update preview data - replace all existing preview data
					previewData.value = [{
						headers: columns,
						displayedRows: resultData.slice(0, 5),
						totalRows: resultData.length
					}];
					
					headers.value = columns;
					rows.value = resultData;
					
					console.log('Updated preview data for statistical', previewData.value);
				} 
				else if (processedData.value.type === 'table') {
					// For transformed data
					if (!processedData.value.data || !Array.isArray(processedData.value.data) || processedData.value.data.length === 0) {
						console.error('No valid transformation data available');
						alert('No transformation data available for continued modification');
						return;
					}
					
					const transformedData = processedData.value.data;
					const columns = Object.keys(transformedData[0] || {});
					
					console.log('Transformed data before conversion:', transformedData);
					console.log('Columns:', columns);
					
					// Create a single new file representation
					files.value = [new File([], 'transformed_data.csv')];
					
					// Update preview data - replace all existing preview data
					previewData.value = [{
						headers: columns,
						displayedRows: transformedData.slice(0, 5),
						totalRows: transformedData.length
					}];
					
					headers.value = columns;
					rows.value = transformedData;
					
					console.log('Updated preview data for transformed', previewData.value);
				} else {
					console.error('Unknown processed data type:', processedData.value.type);
					alert('Unknown data type for continued modification');
					return;
				}
				
				// Clear the processed data to hide the results section
				processedData.value = null;
				
				// Scroll to the prompt input section and data preview
				nextTick(() => {
					// First scroll to the data preview section
					const previewSection = document.querySelector('.bg-white.rounded-lg.shadow-md.p-6.mb-6');
					if (previewSection) {
						console.log('Scrolling to preview section');
						previewSection.scrollIntoView({ behavior: 'smooth' });
						
						// Then, after a short delay, scroll to the prompt section
						setTimeout(() => {
							const promptSection = document.querySelector('.textarea');
							if (promptSection) {
								console.log('Scrolling to prompt section');
								promptSection.scrollIntoView({ behavior: 'smooth' });
								promptSection.focus();
							} else {
								console.error('Prompt textarea not found');
							}
						}, 500);
					} else {
						console.error('Preview section not found');
						// Just scroll to prompt if preview not found
						const promptSection = document.querySelector('.textarea');
						if (promptSection) {
							promptSection.scrollIntoView({ behavior: 'smooth' });
							promptSection.focus();
						}
					}
				});
				
			} catch (error) {
				console.error('Error in continueModification:', error);
				console.error('Error stack:', error.stack);
				alert('An error occurred while setting up for continued modifications. Please try again.');
			}
		};
		
		// Save chart to user's collection
		const saveToCollection = () => {
			// This would be implemented to save the chart to the user's collection
			console.log('Save to collection');
		};
		
		// Initial setup
		onMounted(() => {
			console.log('Component mounted');
			
			try {
				// Check if we have processed data in the store
				const storeProcessedData = dataStore.$state.processedData;
				if (storeProcessedData) {
					console.log('Found processed data in store:', storeProcessedData);
					
					// Handle it based on the type
					if (storeProcessedData.type === 'chart') {
						const datasets = storeProcessedData.config.data.datasets;
						const labels = storeProcessedData.config.data.labels;
						
						// Create a format that can be displayed in the preview table
						const data = labels.map((label, index) => {
							const row = { Category: label };
							datasets.forEach((dataset, datasetIndex) => {
								row[dataset.label || `Series ${datasetIndex + 1}`] = dataset.data[index];
							});
							return row;
						});
						
						const columns = ['Category', ...datasets.map((d, i) => d.label || `Series ${i + 1}`)];
						
						previewData.value = [{
							headers: columns,
							displayedRows: data.slice(0, 5),
							totalRows: data.length
						}];
						
						headers.value = columns;
						rows.value = data;
						
						// Create dummy File objects
						files.value = [new File([], 'visualization_data.csv')];
						
						console.log('Initialized from visualization data in store');
					} 
					else if (storeProcessedData.type === 'statistical_result') {
						let resultData = storeProcessedData.result;
						
						// Handle different result formats
						if (Array.isArray(resultData)) {
							// Already in array format
						} else if (typeof resultData === 'object' && resultData !== null) {
							// Convert object to array format
							resultData = [resultData];
						} else {
							console.error('Unexpected statistical result format in store');
							return;
						}
						
						if (resultData.length === 0) {
							console.error('No statistical data available in store');
							return;
						}
						
						const columns = Object.keys(resultData[0] || {});
						
						previewData.value = [{
							headers: columns,
							displayedRows: resultData.slice(0, 5),
							totalRows: resultData.length
						}];
						
						headers.value = columns;
						rows.value = resultData;
						
						// Create dummy File objects
						files.value = [new File([], 'statistical_data.csv')];
						
						console.log('Initialized from statistical data in store');
					} 
					else if (storeProcessedData.type === 'table') {
						// Handle transformed data from the new agent workflow
						if (!storeProcessedData.data || !Array.isArray(storeProcessedData.data) || storeProcessedData.data.length === 0) {
							console.error('No valid transformation data in store');
							return;
						}
						
						const transformedData = storeProcessedData.data;
						const columns = Object.keys(transformedData[0] || {});
						
						previewData.value = [{
							headers: columns,
							displayedRows: transformedData.slice(0, 5),
							totalRows: transformedData.length
						}];
						
						headers.value = columns;
						rows.value = transformedData;
						
						// Create dummy File objects
						files.value = [new File([], 'transformed_data.csv')];
						
						console.log('Initialized from transformed data in store');
					}
					
					// Clear the processed data from the store
					dataStore.$state.processedData = null;
				}
			} catch (error) {
				console.error('Error in mounted hook:', error);
			}
			
			if (processedData.value?.config) {
				updateChart();
			}
		});
		
		return {
			files,
			previewData,
			userPrompt,
			processedData,
			loading,
			chartCanvas,
			chartInstance,
			activePreviewTab,
			headers,
			rows,
			handleFileUpload,
			loadPreviewData,
			processFilePreview,
			removeFile,
			formatFileSize,
			processData,
			goToDashboard,
			updateChart,
			createChart,
			formatCurrency,
			downloadChartImage,
			downloadData,
			downloadStatisticalData,
			continueModification,
			saveToCollection
		};
	}
};
</script>

<style>
/* Smooth transitions for all interactive elements */
.btn, input, select, textarea, .card {
	transition: all 0.2s ease;
}

/* Better focus styles */
.input:focus, .select:focus, .textarea:focus {
	border-color: #000;
	box-shadow: 0 0 0 2px rgba(var(--p), 0.2);
}

/* Chart container styling */
.chart-container {
	position: relative;
	height: 400px;
	width: 100%;
}

/* Animation for uploaded files */
@keyframes slide-in {
	0% {
		opacity: 0;
		transform: translateY(10px);
	}
	100% {
		opacity: 1;
		transform: translateY(0);
	}
}

.space-y-2 > * {
	animation: slide-in 0.3s ease-out forwards;
}
</style>