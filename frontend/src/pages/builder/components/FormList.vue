<template>
  <!-- <div class="border-2 rounded-lg border-gray-400 h-full m-4 drop-shadow-lg"> -->
	<div>
	<div class="w-full px-4 py-6">
	  <!-- <Button
	class="w-full py-5"
		:variant="'solid'"
		theme="gray"
		size="sm"
		label="Add New Form"
		:loading="false"
		:loadingText="null"
		:disabled="false"
		:link="null"
	  >
		<span class="text-xl"> + </span> Add New Form
	  </Button> -->
	  <div class="mb-3">
		  <TextInput type="text" placeholder="Search Here">
			<template #prefix>
			  <FeatherIcon class="w-4" name="search" />
			</template>
		  </TextInput>
	  </div>
	  <Popover>
		<template #target="{ togglePopover }">
			<Button
			class="w-full py-5"
			:variant="'solid'"
			theme="gray"
			size="sm"
			label="Add New Form"
			:loading="false"
			:loadingText="null"
			:disabled="false"
			:link="null"
			@click="togglePopover()">
			<div class="flex items-center">
				<FeatherIcon name="plus" class="w-5 h-5 mr-2" />
				Add New Form
			</div>
			</Button>
		</template>
		<template #body-main>
			<div class="p-2 mt-2">
				<Input type="text" label="Form Name" v-model="formModel.form_name"/>
			</div>
			<!-- <div class="p-2">
				<FormControl
					:type="'search'"
					size="md"
					variant="subtle"
					placeholder="Placeholder"
					:disabled="false"
					label="Label"
					v-model="inputValue"
				/>
			</div> -->
			<div class="p-2">
				<FormControl
					type="autocomplete"
					:options="props.doctypeList.data"
					size="md"
					variant="subtle"
					placeholder="Select DocType"
					:disabled="false"
					label="DocType"
					v-model="formModel.doctype_name"
					class="w-full"
				/>
			</div>
			<div class="mt-3 mb-4 px-2">
				<Button variant="solid" theme="gray" class="w-full" @click="createForm">
					Save
				</Button>
			</div>
		</template>
	</Popover>
	</div>
	<!-- <div v-if="formList.length" class=""> -->
		<div v-for="form in props.pwaForm.data" :key="form.doctype">
			<div   @click="handleFormFields(form)">
				<FormItem :item="form" />
			</div>
		<!-- </div> -->
	</div>
  </div>
</template>

<script setup>
import { Button, Popover, Autocomplete, FormControl, FeatherIcon, TextInput } from 'frappe-ui';
import { createListResource } from 'frappe-ui';
import FormItem from './FormItem.vue';
import { computed, reactive, ref } from 'vue';

let formList = ref([])

const emit = defineEmits([
  'clicked'
])

function handleFormFields(doctype) {
  console.log("=======================================")
  // isExpanded.value =!isExpanded.value\
  emit("clicked",doctype)
}

let props = defineProps({
	doctypeList: {
		type: Object,
        required: true,
	},
	pwaForm: {
		type: Object,
        required: true,
	}
})

let formModel = reactive({
	form_name : "",
	doctype_name: Object,
})

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

// let pwaForm = createListResource({
// 	doctype: "PWA-Form",
// 	fields: ['form_name', 'doctype_name'],
// 	transform(data) {
// 		console.log(data)
// 		let transformData = []
// 		data.map(doc => {
// 			transformData.push({
// 				title: doc.form_name,
//                 // status: doc.status,
//                 doctype: doc.doctype_name,
//                 // id: doc.name,
//                 // ...doc
// 			})
// 		})
// 		formList.value = transformData
// 	}
// })

// pwaForm.reload()

let pwaForm = createListResource({
	doctype: "PWA DocType",
})


let createForm = () => {
	pwaForm.insert.submit({
		title: formModel.form_name,
		doctype_name: formModel.doctype_name.value,
	}).then(r => {
	console.log(r)
	window.location.reload()
})
}

// let doctype = computed(() => {
// 	console.log(doctypeList.data)
// 	if(doctypeList.lenght) {
// 		return doctypeList.data.map(doc => {
// 				return { label: doc.name, value: doc.name }
// 			}
// 		)
// 	}
// })
const listOfForms = [
	{
		title: "Form 1",
        status: "Active",
		doctype: "Todo"
	},
	{
		title: "Form 2",
        status: "Active",
		doctype: "Todo"
	},
	{
		title: "Form 3",
        status: "Active",
		doctype: "Todo"
	},
	{
		title: "Form 4",
        status: "Active",
		doctype: "Todo"
	},
	{
		title: "Form 5",
        status: "Active",
		doctype: "Todo"
	},
	{
		title: "Form 6",
        status: "Active",
		doctype: "Todo"
	}
]

</script>
