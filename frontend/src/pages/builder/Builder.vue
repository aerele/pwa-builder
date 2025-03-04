<template>
  <div class="h-screen w-screen main flex flex-col main">
    <div v-if="!projectDoc.doc?.project_title" class="h-full flex items-center justify-center">
      <Spinner class="w-10" />
    </div>
    <div v-else>
      <div class="sticky top-0 bg-white shadow-md z-10 p-5 flex justify-between">
        <h1 class="text-3xl">{{ projectDoc.doc.project_title }}</h1>
        <div>
          <Button variant="solid" theme="gray" size="md" @click="exportProject">Export</Button>
        </div>
      </div>
      <div class="flex flex-row h-[92vh] justify-between overflow-hidden">
        <div class="h-full w-[20%] m-4 drop-shadow-lg overflow-y-auto bg-white mt-0 ml-0">
          <FormList :doctypeList="doctypeList" :pwaForm="pwaForm" @clicked="handleFormFields" :id="props.id" />
        </div>
        <div class="w-[30%] h-fit mx-4 mt-4 drop-shadow-lg rounded-lg bg-white">
          <div v-if="formData.doctype_name" class="flex justify-between items-center mt-2 shadow-sm sticky top-0 bg-white border-b px-3 py-2 z-10">
            <h2 class="text-2xl">{{ formData.doctype_name }}</h2>
            <Button variant="solid" theme="gray" size="md" @click="setFieldList">Save</Button>
          </div>
          <div class="min-h-[100px] max-h-[84vh] overflow-y-auto scrollBar">
            <BuilderCanvas :formName="formData.doctype_name" :fieldList="fieldList" :childList="childData" @handleDelete="deleteField" @handleSave="setFieldList" />
          </div>
        </div>
        <div class="h-[92vh] w-[20%] drop-shadow-lg overflow-y-auto scrollBar bg-white">
          <div v-if="spinner" class="h-full flex items-center justify-center">
            <Spinner class="w-8" />
          </div>
          <FieldList :fieldSource="fields" />
        </div>
      </div>
    </div>

    <div v-if="toastMessage" class="fixed bottom-4 right-4 bg-gray-800 text-white py-2 px-4 rounded-lg shadow-lg z-50">
      <span v-html="toastMessage"></span>
    </div>    
  </div>
</template>

<script setup>
import FormList from './components/FormList.vue'
import BuilderCanvas from './components/BuilderCanvas.vue'
import FieldList from './components/FieldList.vue'
import { ref } from 'vue'
import { createListResource, createResource, createDocumentResource } from 'frappe-ui'
import { Button, Spinner } from 'frappe-ui'

let formList = ref([])
let spinner = ref(false)
let fieldList = ref([])
let childData = ref({})
let checkNow = ref(false)
const toastMessage = ref("") 
const repoUrl = ref("")

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
})

let doctypeList = createListResource({
  doctype: "DocType",
  fields: ["name"],
  pageLength: "*",
  transform(data) {
    return data.map(doc => ({ label: doc.name, value: doc.name }))
  }
})
doctypeList.reload()

let pwaForm = createListResource({
  doctype: "PWA DocType",
  fields: ['title', 'doctype_name', "name"],
  filters: { 'project_name': props.id },
  transform(data) {
    formList.value = data.map(doc => ({
      title: doc.title,
      doctype: doc.doctype_name,
    }))
  }
})
pwaForm.reload()

async function handleFormFields(doc) {
  spinner.value = true

  let formFields = createResource({
    url: 'pwa_builder.api.get_doc',
    params: { doctype: 'PWA DocType', docname: doc.name },
    transform(data) {
      fieldList.value = data.field_list ? JSON.parse(data.field_list).pwa_form_fields : []
    },
  })
  await formFields.reload()

  let getFields = createResource({
    url: 'pwa_builder.api.get_meta',
    params: { doctype: doc.doctype_name, project: props.id },
    transform(data) {
      let dataFields = data.fields.filter(item => !expectFields.includes(item.fieldtype) && !expectFields.includes(item.fieldname))

      dataFields.forEach(async (item) => {
        if (item.fieldtype === 'Table') {
          await getChildFields(item)
        }
      })

      let transformData = fieldList.value.length
        ? dataFields.filter(item1 => !fieldList.value.some(item2 => item2.fieldname === item1.fieldname))
        : dataFields

      formData.value = {
        form_name: doc.title,
        name: doc.name,
        doctype_name: doc.doctype_name,
        is_submittable: data.is_submittable,
        pwa_form_fields: fieldList.value,
      }

      fields.value = transformData
      fieldSearch.value = transformData
      spinner.value = false
    }
  })
  getFields.reload()
}

async function exportProject() {
  checkNow.value = true

  let check_repo = createResource({
    url: 'pwa_builder.api.get_repo',
    params: { repo_name: projectDoc.doc.project_title },
  })
  await check_repo.reload()

  const response = check_repo.data

  if (response?.status) {
    repoUrl.value = response.message
    showToast(`Project is already exported to Git: <a href="${repoUrl.value}" target="_blank" class="text-blue-500 underline">${repoUrl.value}</a>`)
  }
  else if(response?.message === "Something went wrong"){
    showToast("Something went wrong while checking repo. Check logs for more information")
  }
  else {
    let export_project = createResource({
      url: 'pwa_builder.api.export_project',
      params: { project_name: props.id },
    })
    await export_project.reload()

    showToast(`Exported! Check Scheduler and PWA-Project for more details.`)
  }
}

function setFieldList() {
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
    params: { doctype: element.options, project: props.id },
    transform(data) {
      let dataFields = data.fields.filter(item => !expectFields.includes(item.fieldtype) && !expectFields.includes(item.fieldname))

      childData.value = {
        ...childData.value,
        [element['fieldname']]: dataFields
      }
    }
  })
  await getfields.reload()
}

function deleteField(field) {
  let index = fieldList.value.findIndex(item => item.fieldname === field.fieldname)
  fieldList.value.splice(index, 1)
  sort_fieldlist(field)
}

function sort_fieldlist(data) {
  for (let i = 1; i <= fields.value.length; i++) {
    if (data.idx === i) {
      fields.value.splice(i - 1, 0, data)
      break
    }
  }
}

function showToast(message) {
  toastMessage.value = message
  setTimeout(() => toastMessage.value = "", 8000) 
}
</script>

<style scoped>
.main {
  background-color: #f6f9fc;
}
.scrollBar::-webkit-scrollbar {
  width: 5px;
  background-color: white;
}
.scrollBar::-webkit-scrollbar-thumb {
  background-color: #cfcdcd;
  border-radius: 5px;
}
</style>