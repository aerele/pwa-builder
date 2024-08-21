<template>
  <div class="h-screen w-screen main flex flex-col main">
    <div class="sticky top-0 bg-white shadow-md z-10 p-5 flex justify-between">
      <!-- <h1>{{ props.id }}</h1>hgjbknlmjhvgchvjb -->
      <h1 class="text-3xl">{{ projectDoc.doc.project_title }}</h1>
      <div>
        <Button variant="solid" theme="gray" size="md" @click="exportProject">Export</Button>
      </div>
    </div>
    <div class="flex flex-row h-[92vh] justify-between overflow-hidden">
      <div class=" h-full w-[20%] m-4 drop-shadow-lg overflow-y-auto formList">
        <FormList :doctypeList="doctypeList" :pwaForm="pwaForm" @clicked="handleFormFields" />
      </div>
      <div class="w-[30%] h-fit mx-4 mt-4 drop-shadow-lg rounded-lg formList">
        <div v-if="formData.doctype_name" class="flex justify-between items-center shadow-sm sticky top-0 bg-white border-b px-3 py-2 z-10">
          <h2 class="text-2xl">{{ formData.doctype_name }}</h2>
          <Button variant="solid" theme="gray" size="md" @click="handleSave">Save</Button>
        </div>
        <!-- <div class=""> -->
          <div class=" min-h-[100px] max-h-[70vh] overflow-y-auto scrollBar">
            <BuilderCanvas class="" :formName="formData.doctype_name" :fieldList="fieldList" @handleSave="setFieldList" />
          </div>
          <div v-if="!fieldList.length" class=" relative h-44 flex justify-center items-center">
            Drag Fields Here
          </div>
        <!-- </div> -->
      </div>
      <div class=" h-full w-[20%] m-4 drop-shadow-lg overflow-y-auto formList">
        <div v-if="spinner" class="h-full flex items-center justify-center">
          <Spinner class="w-8" />
        </div>
        <FieldList :fieldSource="fields.pwa_form_fields" />
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
import { Button, Spinner } from 'frappe-ui'
import FieldList from './components/FieldList.vue'

let formList = ref([])
let spinner = ref(false)
let fieldList = ref([])

const fields = ref({})
let formData = ref({})

let expectFields = ['Section Break', 'Column Break', 'Tab Break', 'rgt', 'lft', 'old_parent']
const props = defineProps({
  id : {
    type : String,
    required : true
  }
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
    url: "pwa_builder.api.get_doc",
    params: {doctype: "PWA DocType", docname: doc.name},
    transform(data) {
      console.log("================data",data)
      let transformData;
      if(data.field_list) {
        let transformData = JSON.parse(data.field_list)
        console.log("================data",transformData)
        // demo.value = transformData.pwa_form_fields
        fieldList.value = transformData.pwa_form_fields
        // demo.value = data.field_list
      }
      else {
        fieldList.value = []
      }
      return transformData
    }
  })

  await formFields.reload()

  console.log(formFields, "000000000000000000000000000000000000000000")
  
  let getFields = createResource({
    url: "pwa_builder.api.get_meta",
    params: {doctype: doc.doctype_name, project : props.id},
    transform(data) {
      console.log(data, "data")
      let transformData;
      let dataFields;
      if(data) {
        console.log("fiedlist +++++++++++++++++++++++++++++++++++++++", fieldList.value)
        console.log("fiedlist +++++++++++++++++++++++++++++++++++++", data)
        dataFields = data.fields.filter((item) => !expectFields.includes(item.fieldtype))
        dataFields = dataFields.filter((item) => !expectFields.includes(item.fieldname))
        if(fieldList.value.length) {
          transformData = dataFields.filter((item1) => !fieldList.value.some(item2 => item2.fieldname === item1.fieldname))
        }
        else {
          transformData = dataFields
        }
        console.log(transformData, " +++++++++++++++++++++++++++++++++++++++", transformData)
        // return transformData
      }
      formData.value = {form_name : doc.title, name : doc.name, doctype_name: doc.doctype_name, is_submittable: data.is_submittable, pwa_form_fields: fieldList.value}
      fields.value = { pwa_form_fields : transformData }
      console.log("fields  ========================= value",fields.value)
      spinner.value = false
    }
  })
  // formDoc.reload()
  getFields.reload()
}


function setFieldList() {
  console.log(fieldList.value)
  if(fieldList.value) {
    formData.value.pwa_form_fields = fieldList.value
  }
  let setValue = createResource({
    url: "pwa_builder.api.set_value",
    params: {doctype: "PWA DocType", docname: formData.value.name, fieldname: "field_list", value: formData.value}
  })
  setValue.reload()
}

function exportProject() {
  console.log("Export Project");
  let exportProject = createResource({
    url: "pwa_builder.api.export_project",
    params: { project_name: props.id }
  });
  exportProject.reload()
}
</script>
<style scoped>
.main {
  background-color: #f6f9fc;
}
.formList {
  background-color: white;
  /* height: auto; */
  /* min-height: 44px; */
}
.hie {
  min-height: 50px;
}
.scrollBar::-webkit-scrollbar{
  width: 5px;
  background-color: white;
  /* overflow: auto; */
}

.scrollBar::-webkit-scrollbar-thumb{
  background-color: #cfcdcd;
  width: 5px;
  border-radius: 5px;
}

.scrollBar::-webkit-scrollbar-thumb:hover{
  background-color: rgb(180, 176, 176);
  width: 5px;
}

.drag{
  margin-top: -200px;
}
</style>

