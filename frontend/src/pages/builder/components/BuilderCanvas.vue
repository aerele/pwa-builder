<template>
  <div
    class="border-dashed border-2 rounded-lg border-gray-400 h-full w-full p-6 m-4 drop-shadow-lg"
  >
    <draggable :list="fieldList" group="listOfFields" @change="log" item-key="fieldname">
      <template #item="{ element }">
        <Button
          class="w-full m-2"
          :variant="'subtle'"
          theme="gray"
          size="sm"
          :label="element.label"
          :loading="false"
          :loadingText="null"
          :disabled="false"
          :link="null"
        >
          {{ element.label }}
		</Button>
      </template>
    </draggable>
  </div>
</template>

<script setup>
import draggable from 'vuedraggable'
import { Button } from 'frappe-ui'
import { ref } from 'vue' // Ensure you import defineProps

// Define props
const { fieldList } = defineProps(['fieldList'])
// let buildedFields = ref([
//   {
//     fieldname: 'basic_info',
//     fieldtype: 'Section Break',
//     label: 'Name and Type',
//     oldfieldtype: 'Section Break',
//     options: 'fa fa-user',
//   },
//   {
//     bold: 1,
//     fieldname: 'customer_name',
//     fieldtype: 'Data',
//     in_global_search: 1,
//     label: 'Full Name',
//     no_copy: 1,
//     oldfieldname: 'customer_name',
//     oldfieldtype: 'Data',
//     reqd: 1,
//     search_index: 1,
//   },
//   {
//     fieldname: 'date',
//     fieldtype: 'Date',
//     label: 'Date',
//   },
// ])
// let fieldList = ref([
//   {
//     fieldname: 'basic_info',
//     fieldtype: 'Section Break',
//     label: 'Name and Type',
//     oldfieldtype: 'Section Break',
//     options: 'fa fa-user',
//   },
//   {
//     bold: 1,
//     fieldname: 'customer_name',
//     fieldtype: 'Data',
//     in_global_search: 1,
//     label: 'Full Name',
//     no_copy: 1,
//     oldfieldname: 'customer_name',
//     oldfieldtype: 'Data',
//     reqd: 1,
//     search_index: 1,
//   },
//   {
//     fieldname: 'date',
//     fieldtype: 'Date',
//     label: 'Date',
//   },
// ])
// Log function
const log = function (evt) {
  window.console.log('recieved', fieldList)
}
</script>

<style scoped>
/* Add any scoped styles here if necessary */
</style>
