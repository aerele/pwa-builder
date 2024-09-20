<template>
	<div>
	<div class="w-full px-4 py-6">
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
		<div v-for="form in props.pwaForm.data" :key="form.doctype">
			<div   @click="handleFormFields(form)">
				<FormItem :item="form" />
			</div>
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
  'clicked', 'create-form'
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
	},
	id: {
		type: String,
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


let pwaForm = createListResource({
	doctype: "PWA DocType",
})


let createForm = () => {
	pwaForm.insert.submit({
		title: formModel.form_name,
		doctype_name: formModel.doctype_name.value,
		project_name: props.id,
	}).then(r => {
	console.log(r)
	window.location.reload()
})

}



</script>
