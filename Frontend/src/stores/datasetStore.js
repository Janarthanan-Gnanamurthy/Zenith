import { defineStore } from 'pinia'

export const useDataStore = defineStore('data', {
  state: () => {
    // Try to load initial state from sessionStorage
    const storedData = sessionStorage.getItem('dataStore')
    return storedData ? JSON.parse(storedData) : {
      files: [],
      previewData: [],
      headers: [],
      rows: [],
      processedData: null
    }
  },
  
  actions: {
    setData(files, previewData, headers, rows) {
      this.files = files
      this.previewData = previewData
      this.headers = headers
      this.rows = rows
      
      // Save to sessionStorage
      sessionStorage.setItem('dataStore', JSON.stringify({
        files: this.files,
        previewData: this.previewData,
        headers: this.headers,
        rows: this.rows,
        processedData: this.processedData
      }))
    },
    
    setProcessedData(processedData) {
      this.processedData = processedData
      
      // Update sessionStorage
      const currentData = JSON.parse(sessionStorage.getItem('dataStore') || '{}')
      currentData.processedData = processedData
      sessionStorage.setItem('dataStore', JSON.stringify(currentData))
    },
    
    clearData() {
      this.files = []
      this.previewData = []
      this.headers = []
      this.rows = []
      this.processedData = null
      
      // Clear from sessionStorage
      sessionStorage.removeItem('dataStore')
    }
  }
})