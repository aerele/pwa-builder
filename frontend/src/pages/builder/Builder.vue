<template>
  <div class="h-screen w-screen main flex flex-col main">
    <div v-if="!projectDoc.doc?.project_title" class="h-full flex items-center justify-center">
      <Spinner class="w-10" />
    </div>
    <div v-else>
      <div class="sticky top-0 bg-white shadow-md z-10 p-5 flex justify-between">
        <div class=" flex items-center">
          <h1 class="text-3xl font-semibold ">{{ projectDoc.doc.project_title }}</h1>
          <FeatherIcon name="folder" class=" w-6 h-6 ml-2 font-semibold"/>
        </div>
        <div class="flex">
          <div v-if="formList.length && !is_validated" class="pr-2">
            <Button variant="solid" theme="gray" size="md" @click="validateForms"
            >
              <div class="flex items-center">
                <FeatherIcon name="check-square" class="w-4 h-4 mr-2" />
                Validate
              </div>
            </Button>
          </div>
          <div v-if="is_validated && !checkNow" class="pr-2">
            <Button variant="solid" theme="gray" size="md" @click="exportProject"
              >
              <div class="flex items-center">
                Export
                <FeatherIcon name="chevrons-right" class="w-4 h-4 ml-2" />
              </div>
              </Button>
          </div>
          <div class="pr-2" v-if="projectdoc.github_repository_url == '' && checkNow">
            <Button variant="solid" theme="gray" size="md" @click="check()"
            >
            <div class="flex items-center">
              <FeatherIcon name="repeat" class="w-4 h-4 mr-2" />
              Check Now
            </div>
            </Button>
          </div>
          <div v-if="projectdoc.github_repository_url != '' && repo">
            <Button variant="solid" theme="gray" size="md"
            >
              <div class="flex items-center">
                <a :href="projectdoc.github_repository_url" target="_blank">Go to Repo</a>
                <FeatherIcon name="arrow-right" class="w-4 h-4 ml-2" />
              </div>
            </Button>
          </div>
        </div>
      </div>
      <div class="flex flex-row h-[92vh] justify-between overflow-hidden">
        <div class=" h-full w-[20%] m-4 drop-shadow-lg overflow-y-auto bg-white mt-0 ml-0">
          <FormList :doctypeList="doctypeList" :pwaForm="pwaForm" @project_id="handleProjectId" @clicked="handleFormFields" :id="props.id" />
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
      <Dialog v-model="dialog">
        <template #body-title>
          <h3 class="font-bold">Form Status</h3>
        </template>
        <template #body-content>
          <div>
            <div v-for="form in formList" :key="form.doctype">
              <div v-if="validate.success == true" class="mb-4 flex justify-between">
                <span class=" font-medium text-gray-700">{{ form.doctype }}</span> 
                <Badge :variant="'subtle'" theme="green" size="lg" label="Badge">Success</Badge>
              </div>
              <div v-else>
                <div v-if="validate.forms_with_missing_fields[form.doctype]">{{ form.doctype }} - Some Mandatory Fields are missing{{ validate.forms_with_missing_fields[form.doctype][form.doctype] }}</div>
              </div>
            </div>
          </div>
        </template>
      </Dialog>
    </div>
  </div>
</template>

<script setup>
import FormList from './components/FormList.vue'
import BuilderCanvas from './components/BuilderCanvas.vue'
import Draggable from 'vuedraggable'
import { ref } from 'vue'
import { createListResource, createResource, createDocumentResource } from 'frappe-ui'
import { Button, Spinner, Dialog, toast, Badge, FeatherIcon } from 'frappe-ui'
import FieldList from './components/FieldList.vue'

let formList = ref([])
let spinner = ref(false)
let fieldList = ref([])
let childData = ref({})
let checkNow = ref(false)
let repo = ref(false)
const fields = ref([])
let is_validated = ref(false)
let dialog = ref(false)
let fieldSearch = ref([])
let validate = ref()
let formData = ref({})
let childList = ref([])
let projectdoc = ref({github_repository_url: ''})
let docvalue = ref("")
let project_id = ref('')

let expectFields = ['Section Break', 'Column Break', 'Tab Break', 'Geolocation', 'Button', 'rgt', 'lft', 'old_parent']
const props = defineProps({
  id: {
    type: String,
    required: true,
  },
})

const get_number_card = async () => {
  const docs = await  createListResource({
    doctype: "Number Card",
    fields: ["name"],
    pageLength: "*",
  })
  await docs.reload()  
  return docs.data
}


async function check() {
  await  projectDoc.reload()
  repo.value = true
}

let projectDoc = createDocumentResource({
  doctype: "PWA-Project",
  name: props.id,
  fields: ["*"],
  onSuccess(data) {
    projectdoc.value = data
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
	fields: ['title', 'doctype_name', "name", "is_validated"],
  filters: {'project_name': props.id},
	transform(data) {
		let transformData = []
		data.map(doc => {
			transformData.push({
				      title: doc.title,
              doctype: doc.doctype_name,
			})
      if (doc.is_validated == 0){
        is_validated.value = false
      }
		})
		formList.value = transformData
	}
})

pwaForm.reload()


async function handleProjectId(projectid) {
    project_id.value = projectid
}
async function handleFormFields (doc) {
  if (doc === "Dashboard") {

    const field_list = []
    const data = await get_number_card_data();
    const fieldLists = data?.[0]?.field_list ? JSON.parse(data[0].field_list) : null;
    const existingFields = fieldLists?.pwa_form_fields ?? [];
    fieldList.value = fieldLists?.pwa_form_fields ?? [];

    const existingFieldNames = new Set(existingFields.map(field => field.fieldname));

    const docs = await get_number_card();

    let idx = fieldList.value.length
    docs.forEach(element => {
        if (!existingFieldNames.has(element.name)) {
            let field = {
                fieldtype: "Number Card",
                fieldname: element.name,
                label: element.name,
                idx: idx
            };
            idx++
            field_list.push(field);
        }
    });

    const transformData = {
        doctype_name: "Dashboard",
        form_name: "Dashboard",
        is_submittable: 0,
        pwa_form_fields: field_list,
    };


    formData.value = {
        form_name: "Number Card",
        name: "Number Card",
        doctype_name: "Dashboard",
        is_submittable: 0,
        pwa_form_fields: existingFields,
    };


    fields.value = transformData.pwa_form_fields;
    Dash
    return transformData;
  }
  if(doc.doctype_name == formData.value.doctype_name){
    return
  }
  spinner.value = true
  let formFields = createResource({
    url: "frappe.client.get_list",
    params: { doctype: "PWA DocType", filters: {"name": doc.name}, fields: ["name","field_list"]},
    transform(data) {
      let transformData;
      if(data.length) {
        if(data[0].field_list != '{}'){
          transformData = JSON.parse(data[0].field_list)
          fieldList.value = []
          if ("pwa_form_fields" in transformData)
          fieldList.value = transformData.pwa_form_fields
        }
      }
      else{
        fieldList.value = []
      }
      return transformData
    }
  })

  await formFields.reload()

  let getFields = createResource({
    url: 'pwa_builder.api.get_meta',
    params: { doctype: doc.doctype_name, project: props.id },
    transform(data) {
      let transformData;
      let dataFields;
      if(data) {
        dataFields = data.fields.filter((item) => !expectFields.includes(item.fieldtype))
        dataFields = dataFields.filter((item) => !expectFields.includes(item.fieldname))
        dataFields.map(async(item) => {
          if(item.fieldtype == 'Table'){
            await getChildFields(item)
          }
        })
        if(fieldList.value) {
          transformData = dataFields.filter((item1) => !fieldList.value.some(item2 => item2.fieldname === item1.fieldname))
        }
        else {
          transformData = dataFields
        }
      }
      formData.value = {form_name : doc.title, name : doc.name, doctype_name: doc.doctype_name, is_submittable: data.is_submittable, pwa_form_fields: fieldList.value}
      fields.value = transformData
      fieldSearch.value = transformData
      spinner.value = false
    }
  })
  getFields.reload()
}

function sort_fieldlist(data){
  let temp = []
    for(let i = 1; i <= fields.value.length; i++){
      if(data.idx < fields.value[i].idx){
        fields.value.splice(i - 1, 0, data)
        break
      }
    }
}

function deleteField(field) {
  let index = fieldList.value.findIndex(item => item.fieldname === field.fieldname)
  fieldList.value.splice(index, 1)
  sort_fieldlist(field)
}

async function get_number_card_data () {
  let get_dashboard_name =  await createListResource(
        {
          doctype: 'PWA DocType',
          fields: ['name', 'field_list'],
          filters : {
            title: "Dashboard", 
            project_name: project_id
          }
        }
      )
      await get_dashboard_name.reload()
      return  get_dashboard_name.data ? get_dashboard_name.data : null
}

async function setFieldList() {
  if (fieldList.value) {
    formData.value.pwa_form_fields = fieldList.value
  }
  let name = null
  if (formData.value?.doctype_name == "Dashboard"){
      let get_name = await get_number_card_data()
      name = get_name ?  get_name[0]?.name : null
  }

  let setValue = createResource({
    url: 'pwa_builder.api.set_value',
    params: {
      doctype: 'PWA DocType',
      docname: name ? name :  formData.value.name,
      fieldname: 'field_list',
      value: formData.value,
    },
    onSuccess(){
      toast({
				title: "Success",
				text: `Form Saved successfully!`,
				icon: "check-circle",     
				position: "bottom-right",
				iconClasses: "text-green-500",
			})
    },
  })
  await setValue.reload()
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

async function validateForms(){
  let validateForms = createResource({
    url: 'pwa_builder.api.validate_form_fields',
    params: { project_name: props.id },
    transform(data){
      validate.value = data
    }
  })

 await validateForms.reload()
 dialog.value = true
 is_validated.value = true
}

function exportProject() {
  let export_project = createResource({
    url: 'pwa_builder.api.export_project',
    params: { project_name: props.id },
  })
  
  export_project.reload()
  toast({
				title: "Success",
				text: `Exported! Check Scheduler and PWA-Project for more details.`,
				icon: "check-circle",     
				position: "bottom-right",
				iconClasses: "text-green-500",
  })
  checkNow.value = true
  projectdoc.value = {github_repository_url: ''}
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