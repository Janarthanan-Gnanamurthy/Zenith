<template>
<div>
    <h3 class="text-lg font-semibold mb-2">Insight Widget</h3>
    <div>
    <p><strong>Total Records:</strong> {{ rows.length }}</p>
    <p><strong>Columns:</strong> {{ headers.join(', ') }}</p>
    <!-- Additional insights can be added here -->
    </div>
</div>
</template>

<script>
export default {
name: 'InsightWidget',
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
};
</script>

<style scoped>
/* Additional styling if needed */
</style>
