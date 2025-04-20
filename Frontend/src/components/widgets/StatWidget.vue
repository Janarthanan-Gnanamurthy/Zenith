<template>
  <div>
    <div class="grid grid-cols-2 gap-4">
      <div v-for="(stat, index) in statistics" :key="index" class="p-4 bg-gray-50 rounded-lg">
        <div class="text-sm text-gray-500">{{ stat.label }}</div>
        <div class="text-xl font-semibold">{{ stat.value }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatWidget',
  
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

  computed: {
    statistics() {
      const numericColumns = this.headers.map((header, index) => ({
        header,
        index,
        isNumeric: this.isNumericColumn(index)
      })).filter(col => col.isNumeric);

      return numericColumns.map(column => {
        const values = this.rows.map(row => parseFloat(row[column.index])).filter(val => !isNaN(val));
        const sum = values.reduce((acc, val) => acc + val, 0);
        const avg = sum / values.length;
        const max = Math.max(...values);
        const min = Math.min(...values);

        return [
          {
            label: `${column.header} (Avg)`,
            value: avg.toFixed(2)
          },
          {
            label: `${column.header} (Max)`,
            value: max.toFixed(2)
          },
          {
            label: `${column.header} (Min)`,
            value: min.toFixed(2)
          }
        ];
      }).flat();
    }
  },

  methods: {
    isNumericColumn(columnIndex) {
      return this.rows.some(row => 
        !isNaN(parseFloat(row[columnIndex])) && row[columnIndex] !== ''
      );
    }
  }
};
</script>