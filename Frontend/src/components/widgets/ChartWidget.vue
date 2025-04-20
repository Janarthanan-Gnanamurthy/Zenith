<template>
	<div>
		<div class="chart-container" ref="chartContainer">
			<canvas ref="chartCanvas"></canvas>
		</div>
	</div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
	name: 'ChartWidget',

	props: {
		widget: {
			type: Object,
			required: true
		},
		headers: {
			type: Array,
			required: true
		},
		rows: {
			type: Array,
			required: true
		}
	},

	data() {
		return {
			chartInstance: null,
			resizeObserver: null
		};
	},

	created() {
		if (!this.widget.config.xColumn) {
			this.initializeConfig();
		}
	},

	mounted() {
		this.initializeChart();
		this.setupResizeObserver();
	},

	beforeUnmount() {
		this.cleanup();
	},

	watch: {
		'widget.config': {
			deep: true,
			handler() {
				if (this.chartInstance) {
					this.updateChart();
				}
			}
		},
		rows: {
			handler() {
				this.updateChart();
			},
			deep: true
		}
	},

	methods: {
		initializeConfig() {
			const firstNumericColumn = this.headers.findIndex((_, index) => 
				this.isNumericColumn(index)
			);

			const config = {
				...this.widget.config,
				xColumn: 0,
				yColumns: firstNumericColumn !== -1 ? [firstNumericColumn] : []
			};

			this.$emit('update:widget', {
				...this.widget,
				config
			});
		},

		isNumericColumn(columnIndex) {
			return this.rows.some(row => 
				!isNaN(parseFloat(row[columnIndex])) && row[columnIndex] !== ''
			);
		},

		initializeChart() {
			if (!this.rows?.length) return;

			const ctx = this.$refs.chartCanvas.getContext('2d');
			const { labels, datasets } = this.prepareChartData();

			if (this.chartInstance) {
				this.chartInstance.destroy();
			}

			this.chartInstance = new Chart(ctx, {
				type: this.widget.config.chartType || 'bar',
				data: {
					labels,
					datasets
				},
				options: this.getChartOptions()
			});
		},

		prepareChartData() {
			const xColumn = this.widget.config.xColumn || 0;
			const yColumns = this.widget.config.yColumns || [];
			
			const labels = this.rows.map(row => row[xColumn]);
			
			const datasets = yColumns.map((columnIndex, datasetIndex) => ({
				label: this.headers[columnIndex],
				data: this.rows.map(row => parseFloat(row[columnIndex]) || 0),
				backgroundColor: this.getColor(datasetIndex),
				borderColor: this.getColor(datasetIndex),
				borderWidth: 1,
				fill: this.widget.config.chartType === 'line' ? false : true
			}));

			return { labels, datasets };
		},

		getChartOptions() {
			return {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: this.widget.config.title
					},
					legend: {
						position: 'bottom'
					},
					tooltip: {
						mode: 'index',
						intersect: false
					}
				},
				scales: {
					y: {
						beginAtZero: true
					}
				},
				animation: {
					duration: 500
				}
			};
		},

		getColor(index) {
			const colors = [
				'rgba(54, 162, 235, 0.8)',
				'rgba(255, 99, 132, 0.8)',
				'rgba(75, 192, 192, 0.8)',
				'rgba(255, 206, 86, 0.8)',
				'rgba(153, 102, 255, 0.8)',
				'rgba(255, 159, 64, 0.8)'
			];
			return colors[index % colors.length];
		},

		updateChart() {
			this.initializeChart();
		},

		setupResizeObserver() {
			this.resizeObserver = new ResizeObserver(() => {
				if (this.chartInstance) {
					this.chartInstance.resize();
				}
			});
			this.resizeObserver.observe(this.$refs.chartContainer);
		},

		cleanup() {
			if (this.chartInstance) {
				this.chartInstance.destroy();
			}
			if (this.resizeObserver) {
				this.resizeObserver.disconnect();
			}
		}
	}
};
</script>

<style scoped>
.chart-container {
	position: relative;
	height: 300px;
	width: 100%;
	padding: 1rem;
}
</style>