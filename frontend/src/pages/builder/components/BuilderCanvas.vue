<template>
  <div class="w-full p-4">
    <!-- Draggable Drop Area for Field List -->
    <Draggable
      :list="fieldList"
      group="listOfFields"
      @change="log"
      item-key="fieldname"
      class="w-full"
    >
      <template #item="{ element }">
        <div
          class="border p-2 border-white hover:border-black-overlay-400 hover:bg-gray-100 rounded-md cursor-pointer"
          @mouseover="hoverIndex = element.idx"
          @mouseleave="hoverIndex = null"
        >
          <div>
            <div class="flex justify-between items-center px-1">
              <div class="ml-2 text-sm">{{ element.label }}</div>
                <FeatherIcon
                  name="x"
                  :class="['text-white w-4 h-4 p-0.5',hoverIndex == element.idx ? 'text-black hover:bg-white rounded-full' : '']"
                  @click="handleDelete(element)"
                />
            </div>
            <div>
              <component :is="fieldMap[element.fieldtype]" @click="element.fieldtype == 'Table' ? [childDialog(element), dialog = true] : ''" />
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <div
          v-if="!fieldList.length"
          class="drop-area flex justify-center items-center border-dashed border-2 border-gray-400 p-8 rounded-lg"
        >
          <p class="text-gray-500">Drag Fields Here</p>
        </div>
      </template>
    </Draggable>

    <Dialog v-model="dialog" group="listOfChildFields" class="list-group">
      <template #body-title>
        <h3 class="font-semibold">Select Table Columns For <span class="font-bold">{{ childDetails.doctype }}</span></h3>
      </template>
      <template #body-content>
        <div class=" max-h-[80vh] overflow-y-auto border-y scrollBar">
          <Draggable :list="currentChildFields" item-key="fieldname">
              <template #item="{ element }">
                <div class="flex flex-row p-2 my-1 rounded-md hover:bg-gray-100 cursor-grab">
                  <div class=" px-2">
                    <svg fill="#b8bbbc" class="text-2xl" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="20" height="20">
                      <path d="M10 13a1 1 0 1 1 0-2 1 1 0 0 1 0 2Zm0-4a1 1 0 1 1 0-2 1 1 0 0 1 0 2Zm-4 4a1 1 0 1 1 0-2 1 1 0 0 1 0 2Zm5-9a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM7 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM6 5a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z"></path>
                    </svg>
                   </div>
                  <div>
                    <FormControl
                      type="checkbox"
                      size="md"
                      variant="subtle"
                      :disabled="false"
                      :label="element.label"
                      v-model="checkbox[element.fieldname]"
                  />
                  </div>
                </div>
              </template>
             </Draggable>
        </div>
         <div class="flex justify-end mt-2">
            <Button size="md" variant="solid" @click="[updateChildFields(),dialog = false]">Update</Button>
          </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import Draggable from 'vuedraggable';
import { FeatherIcon, Dialog, FormControl } from 'frappe-ui';
import { Button } from 'frappe-ui';
import { reactive, ref } from 'vue';
import Text from '../../../form/components/Text.vue';
import Select from '../../../form/components/Select.vue';
import Int from '../../../form/components/Int.vue';
import Autocomplete from '../../../form/components/Autocomplete.vue';
import DateTime from '../../../form/components/DateTime.vue';
import Date from '../../../form/components/Date.vue';
import Checkbox from '../../../form/components/Checkbox.vue';
import Attach from '../../../form/components/FileUploader.vue';
import Textarea from '../../../form/components/TextArea.vue';
import Table from '../../../form/components/Table.vue';
import FieldList from './FieldList.vue';
import Input from 'frappe-ui/src/components/Input.vue';

// const { fieldList, formName } = defineProps(['fieldList', 'formName']);
let props = defineProps({
  fieldList: {
    type: Array,
  },
  formName: {
    type: String,
  },
  childList: {
    type: Object,
  }
})
let hoverIndex = ref(null);
let checkbox = reactive({})
let currentChildFields = ref([])
let childDetails = reactive({
  fieldname: '',
  doctype: '',
  index: 0,
})
let dialog = ref(false)
let emit = defineEmits(['handle-save', 'handle-delete']);

function handleSave() {
  console.log('handleSave');
  emit('handle-save');
}

function handleDelete(item) {
  emit('handle-delete', item);
}

async function childDialog(element) {
  dialog.value = true;
  console.log('childDialog', element);

  console.log("childdata",props.childList[element.fieldname])

  console.log(props.fieldList)

  let index = props.fieldList.findIndex(item => item.fieldname === element.fieldname)

  childDetails.doctype = props.childList[element.fieldname][0].parent
  childDetails.fieldname = element.fieldname
  childDetails.index = index

  if(typeof(props.fieldList[index].options) != 'string'){
    console.log(typeof(props.fieldList[index].options), "string==========================")
    // checkbox[props.childList.fieldname] = false;
    // props.fieldList[index].options.map((item) => {
    //   checkbox[item.fieldname] = true;
    // })
    await props.fieldList[index].options.map((item1)  => {
      props.childList[element.fieldname].map((item2) => {
        if(item1.fieldname == item2.fieldname){
          console.log("items111111111111111111111111111111111111111",item1)
          checkbox[item1.fieldname] = true;
        }
        else{
          if(!checkbox[item2.fieldname]){
            checkbox[item2.fieldname] = false;
          }
        }
      })
    })

  }
  else{
    console.log(typeof(props.fieldList[index].options), "typeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
    await props.childList[element.fieldname].map((item) => {
      checkbox[item.fieldname] = false;
    })
  }

  currentChildFields.value = props.childList[element.fieldname]


  // emit('child-dialog', element);
}

function updateChildFields(){
  console.log("update Dialog")
  let childList = []
  currentChildFields.value.map((item) => {
    if(checkbox[item.fieldname]){
      childList.push(item)
    }
  })
  props.fieldList[childDetails.index].options = childList
  console.log(props.fieldList)
}

const fieldMap = {
  Data: Text,
  Attach: Attach,
  'Attach Image': Attach,
  Select: Select,
  Int: Int,
  Autocomplete: Select,
  Dynamic_Link: Select,
  Datetime: DateTime,
  Date: Date,
  Check: Checkbox,
  Text: Text,
  Table: Table,
  'Long Text': Textarea,
  'Small Text': Textarea,
  Float: Int,
  Link: Text,
  Currency: Text,
};

const log = function (evt) {
  window.console.log('received', props.fieldList);
};
</script>

<style scoped>
.drop-area {
  background-color: #f6f9fc;
  transition: background-color 0.2s ease;
}

.drop-area:hover {
  background-color: #e0e7ff;
}

.scrollBar::-webkit-scrollbar{
  width: 5px;
  background-color: white;
  /* overflow: auto; */
}

.scrollBar::-webkit-scrollbar-thumb{
  background-color: white;
  width: 5px;
  border-radius: 5px;
}

.scrollBar::-webkit-scrollbar-thumb:hover{
  background-color: white;
  width: 5px;
}
</style>
