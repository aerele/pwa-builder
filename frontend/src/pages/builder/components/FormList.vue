<template>
  <div class="border-2 rounded-lg border-gray-400 h-full m-4 drop-shadow-lg">
	<div class="w-full px-4 py-6">
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
	  >
		<span class="text-xl"> + </span> Add New Form
	  </Button>
	</div>
	<div class="">
		<div v-for="form in listOfForms" :key="form.doctype">
			<FormItem :item="form" />
		</div>
	</div>
  </div>
</template>

<script setup>
import { Button } from 'frappe-ui';
import FormItem from './FormItem.vue';
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
