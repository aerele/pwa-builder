<template>
  <div class="h-screen w-screen main flex flex-col main">
    <div class="sticky top-0 bg-white shadow-md z-10 p-5 flex justify-between">
      <h1 class="text-3xl">{{ projectDoc.doc.project_title }}</h1>
      <div>
        <Button variant="solid" theme="gray" size="md" @click="exportProject"
          >Export</Button
        >
      </div>
    </div>
    <div class="flex flex-row h-[92vh] justify-between overflow-hidden">
      <div class=" h-full w-[20%] m-4 drop-shadow-lg overflow-y-auto bg-white mt-0 ml-0">
        <FormList :doctypeList="doctypeList" :pwaForm="pwaForm" @clicked="handleFormFields" :id="props.id" />
      </div>
      <div class="w-[30%] h-fit mx-4 mt-4 drop-shadow-lg rounded-lg bg-white">
        <div v-if="formData.doctype_name" class="flex justify-between items-center mt-2 shadow-sm sticky top-0 bg-white border-b px-3 py-2 z-10">
          <h2 class="text-2xl">{{ formData.doctype_name }}</h2>
          <Button variant="solid" theme="gray" size="md" @click="setFieldList">Save</Button>
        </div> 
          <div class=" min-h-[100px] max-h-[84vh] overflow-y-auto scrollBar">
            <BuilderCanvas :formName="formData.doctype_name" :fieldList="fieldList" :childList="childData" @handleDelete="deleteField" @handleSave="setFieldList" />
          </div>
      </div>
      <div class=" h-[92vh] w-[20%] drop-shadow-lg overflow-y-auto scrollBar bg-white">
        <div v-if="spinner" class="h-full flex items-center justify-center">
          <Spinner class="w-8" />
        </div>
        <FieldList :fieldSource="fields" />
      </div>
    </div>
  </div>
</template>

<script setup>
import FormList from './components/FormList.vue'
import BuilderCanvas from './components/BuilderCanvas.vue'
import Draggable from 'vuedraggable'
import { ref } from 'vue'
import { createListResource, createResource, createDocumentResource } from 'frappe-ui'
import { Button, Spinner, } from 'frappe-ui'
import FieldList from './components/FieldList.vue'

let formList = ref([])
let spinner = ref(false)
let fieldList = ref([])
let childData = ref({})

const fields = ref([])
let fieldSearch = ref([])
let formData = ref({})
let childList = ref([])

let expectFields = ['Section Break', 'Column Break', 'Tab Break', 'Geolocation', 'Button', 'rgt', 'lft', 'old_parent']
const props = defineProps({
  id: {
    type: String,
    required: true,
  },
})

let projectDoc = createDocumentResource({
  doctype: "PWA-Project",
  name: props.id,
  fields: ["*"],
  onSuccess(data) {
    console.log(data.project_title)
  },
});

let doctypeList = createListResource({
	doctype: "DocType",
  fields: ["name"],
	pageLength: "*",
	transform(data) {
		return data.map(doc => {
			return { label: doc.name, value: doc.name }
		})
	}
})

doctypeList.reload()

let pwaForm = createListResource({
	doctype: "PWA DocType",
	fields: ['title', 'doctype_name', "name"],
  filters: {'project_name': props.id},
	transform(data) {
		console.log(data)
		let transformData = []
		data.map(doc => {
			transformData.push({
				      title: doc.title,
              doctype: doc.doctype_name,
			})
		})
		formList.value = transformData
	}
})

pwaForm.reload()

async function handleFormFields (doc) {
  spinner.value = true
  console.log("================doc",doc)
  let formFields = createResource({
    url: 'pwa_builder.api.get_doc',
    params: { doctype: 'PWA DocType', docname: doc.name },
    transform(data) {
      console.log('================data', data)
      let transformData
      if (data.field_list) {
        let transformData = JSON.parse(data.field_list)
        console.log('================data', transformData)
        // demo.value = transformData.pwa_form_fields
        fieldList.value = transformData.pwa_form_fields
        // demo.value = data.field_list
      } else {
        fieldList.value = []
      }
      return transformData
    },
  })

  await formFields.reload()

  console.log(formFields, '000000000000000000000000000000000000000000')

  let getFields = createResource({
    url: 'pwa_builder.api.get_meta',
    params: { doctype: doc.doctype_name, project: props.id },
    transform(data) {
      console.log(data, "data")
      let transformData;
      let dataFields;
      if(data) {
        console.log("fiedlist +++++++++++++++++++++++++++++++++++++++", fieldList.value)
        console.log("fiedlist +++++++++++++++++++++++++++++++++++++", data)
        dataFields = data.fields.filter((item) => !expectFields.includes(item.fieldtype))
        dataFields = dataFields.filter((item) => !expectFields.includes(item.fieldname))
        dataFields.map(async(item) => {
          if(item.fieldtype == 'Table'){
            await getChildFields(item)
          }
        })
        if(fieldList.value.length) {
          transformData = dataFields.filter((item1) => !fieldList.value.some(item2 => item2.fieldname === item1.fieldname))
        }
        else {
          transformData = dataFields
        }
        console.log(
          transformData,
          ' +++++++++++++++++++++++++++++++++++++++',
          transformData
        )
        // return transformData
      }
      formData.value = {form_name : doc.title, name : doc.name, doctype_name: doc.doctype_name, is_submittable: data.is_submittable, pwa_form_fields: fieldList.value}
      fields.value = transformData
      fieldSearch.value = transformData
      console.log("fields  ========================= value",fields.value)
      spinner.value = false
    }
  })
  // formDoc.reload()
  getFields.reload()
}

function sort_fieldlist(data){
  console.log(data, "ddddddddddddddddddddddd", data.length)
  let temp = []
    for(let i = 1; i <= fields.value.length; i++){
      if(data.idx == i){
        console.log(data, "dddddddddddddddddd")
        fields.value.splice(i - 1, 0, data)
        break
      }
    }
}

function deleteField(field) {
  console.log("Delete Field", field)
  let index = fieldList.value.findIndex(item => item.fieldname === field.fieldname)
  fieldList.value.splice(index, 1)
  // fields.value.push(field)
  sort_fieldlist(field)
}


function setFieldList() {
  console.log(fieldList.value)
  if (fieldList.value) {
    formData.value.pwa_form_fields = fieldList.value
  }
  let setValue = createResource({
    url: 'pwa_builder.api.set_value',
    params: {
      doctype: 'PWA DocType',
      docname: formData.value.name,
      fieldname: 'field_list',
      value: formData.value,
    },
  })
  setValue.reload()
}

async function getChildFields(element) {
  let getfields = createResource({
    url: "pwa_builder.api.get_meta",
    params: {doctype: element.options, project : props.id},
    transform(data) {
      let transformData = []
      let dataFields;
      dataFields = data.fields.filter((item) => !expectFields.includes(item.fieldtype))
      dataFields = dataFields.filter((item) => !expectFields.includes(item.fieldname))
      console.log("dataFields: " , dataFields)
      if(childData.value){
        childData.value = {...childData.value, [element['fieldname']]: dataFields}
      }
      else{
        childData.value = {[element['fieldname']]: dataFields}
      }
    }
  })

  await getfields.reload()
}

function exportProject() {
  console.log('Export Project')
  let exportProject = createResource({
    url: 'pwa_builder.api.export_project',
    params: { project_name: props.id },
  })
  exportProject.reload()
//   const url = window.URL.createObjectURL(new Blob([response.data]))
  const origin = window.location.origin
  const file = "/files/PWA Demo.zip"
  const link = document.createElement('a')
  link.href = origin + file
//   link.setAttribute('download', 'file.png') //or any other extension
//   document.body.appendChild(link)
  link.click()
}
</script>
<style scoped>
.main {
  background-color: #f6f9fc;
}
.hie {
  min-height: 50px;
}
.scrollBar::-webkit-scrollbar{
  width: 5px;
  background-color: white;
}

.scrollBar::-webkit-scrollbar-thumb {
  background-color: #cfcdcd;
  width: 5px;
  border-radius: 5px;
}

.scrollBar::-webkit-scrollbar-thumb:hover {
  background-color: rgb(180, 176, 176);
  width: 5px;
}

.drag {
  margin-top: -200px;
}
</style>
