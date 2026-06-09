import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useEncouragementStore = defineStore('encouragement', () => {
  const visible = ref(false)
  const encouragementData = ref(null)

  function show(data) {
    encouragementData.value = data
    visible.value = true
  }

  function dismiss() {
    visible.value = false
    encouragementData.value = null
  }

  return { visible, encouragementData, show, dismiss }
})
