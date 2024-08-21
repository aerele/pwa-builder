<template>
  <div class="w-full px-4">
    <!-- <div
      class=" border-2 rounded-lg border-gray-400 h-full w-full p-6 m-4 drop-shadow-lg"
    > -->
    <!-- <div v-if="formName" class="border-b-2 shadow-sm mb-3 px-3">
      <div class="flex justify-between mt-4">
        {{ formName }}
        
        <Button @click="handleSave">Save</Button>
      </div>
    </div> -->
    <!-- <div class="border w-full h-36"> -->
      <!-- <div v-if="!fieldList.length" class="w-full h-full flex items-center justify-center">
          Drag & Drop
      </div> -->
      <Draggable :list="fieldList" group="listOfFields" @change="log" item-key="fieldname"  class=" w-full">
        <template #item="{ element }">
         <div class="mt-4">
           <div class="p-4 border border-gray-400">
            {{ element.label }}
           </div>
         </div>
        </template>
      </Draggable>
    <!-- </div> -->
    </div>
  <!-- </div> -->
</template>

<script setup>
import Draggable from 'vuedraggable'
// import { Button } from 'frappe-ui'
// import { ref } from 'vue'
// import Text from '../../../form/components/Text.vue';
// import Select from '../../../form/components/Select.vue';
// import Int from '../../../form/components/Int.vue';
// import Autocomplete from '../../../form/components/Autocomplete.vue';
// import DateTime from '../../../form/components/DateTime.vue';
// import Date from '../../../form/components/Date.vue';
// import SectionBreak from '../../../form/components/SectionBreak.vue';
// import Checkbox from '../../../form/components/Checkbox.vue';
// import Float from '../../../form/components/Float.vue';
// import Link from '../../../form/components/Link.vue';
// import Currency from '../../../form/components/Currency.vue';
// import Textarea from '../../../form/components/Textarea.vue';
// import Badge from '../../../form/components/Badge.vue';


// Define props
const { fieldList, formName } = defineProps(['fieldList', 'formName'])

let emit = defineEmits(['handle-save'])

function handleSave() {
  console.log("handleSave")
  emit('handle-save')
}

// const fieldMap = {
//   Data: Text,
//   Select: Select,
//   Int: Int,
//   Autocomplete: Autocomplete,
//   Dynamic_Link: Select,
//   Heading: Badge,
//   Datetime: DateTime,
//   Date: Date,
//   'Section Break': SectionBreak,
//   Check: Checkbox,
//   Text: Text,
//   'Long Text': Textarea,
//   'Small Text': Textarea,
//   Float: Float,
//   Link: Link,
//   Currency: Currency,
// }

// const fieldMap = {
//   Data: Text,
//   Select: Select,
//   Int: Int,
//   Autocomplete: Autocomplete,
//   Dynamic_Link: Select,
//   Heading: Badge,
//   Datetime: DateTime,
//   Date: Date,
//   'Section Break': SectionBreak,
//   Check: Checkbox,
//   Text: Text,
//   'Long Text': Textarea,
//   'Small Text': Textarea,
//   Float: Float,
//   Link: Link,
//   Currency: Currency,
// }
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
