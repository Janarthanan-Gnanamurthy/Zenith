<template>
	<div>
		<div class="overflow-x-auto">
			<table class="table w-full">
				<thead>
					<tr>
						<th v-for="header in headers" :key="header" class="px-4 py-2 text-left">
							{{ header }}
						</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(row, index) in paginatedRows" :key="index">
						<td v-for="(cell, cellIndex) in row" :key="cellIndex" class="px-4 py-2">
							{{ cell }}
						</td>
					</tr>
				</tbody>
			</table>
		</div>
		<!-- Pagination -->
		<div v-if="rows.length > pageSize" class="flex justify-between items-center mt-4">
			<div class="text-sm text-gray-600">
				Showing {{ startIndex + 1 }} to {{ Math.min(endIndex, rows.length) }} of {{ rows.length }} entries
			</div>
			<div class="flex gap-2">
				<button 
					@click="currentPage--" 
					:disabled="currentPage === 1"
					class="px-3 py-1 rounded border hover:bg-gray-100 disabled:opacity-50"
				>
					Previous
				</button>
				<button 
					@click="currentPage++" 
					:disabled="currentPage >= totalPages"
					class="px-3 py-1 rounded border hover:bg-gray-100 disabled:opacity-50"
				>
					Next
				</button>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: 'TableWidget',
	
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
			currentPage: 1,
			pageSize: 10
		};
	},

	computed: {
		totalPages() {
			return Math.ceil(this.rows.length / this.pageSize);
		},
		startIndex() {
			return (this.currentPage - 1) * this.pageSize;
		},
		endIndex() {
			return this.startIndex + this.pageSize;
		},
		paginatedRows() {
			return this.rows.slice(this.startIndex, this.endIndex);
		}
	},

	watch: {
		rows() {
			this.currentPage = 1;
		}
	}
};
</script>

<style scoped>
.table {
	@apply min-w-full divide-y divide-gray-200;
}
.table th {
	@apply bg-gray-50 font-medium text-gray-500 uppercase tracking-wider;
}
.table td {
	@apply whitespace-nowrap text-sm text-gray-900;
}
.table tr:nth-child(even) {
	@apply bg-gray-50;
}
</style>