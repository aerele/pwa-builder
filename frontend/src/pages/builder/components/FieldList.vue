<template>
  <!-- <div class="border-2 rounded-lg border-gray-400 h-full m-4 drop-shadow-lg"> -->
    <div class=" px-4">
    <div v-if="fieldSource" class="w-full py-6" placeholder="Search Here">
      <TextInput type="text" placeholder="Search Here">
        <template #prefix>
          <FeatherIcon class="w-4" name="search" />
        </template>
      </TextInput>
    </div>
    <!-- <div>
		<div v-for="item in fieldList" :key="item.fieldname" class="px-6 py-2 w-full">

        <Button
			class="w-full"
          :variant="'subtle'"
          theme="gray"
          size="sm"
          :label="item.label"
          :loading="false"
          :loadingText="null"
          :disabled="false"
          :link="null"
        >
          {{ item.label }}
        </Button>
      </div>
    </div> -->
    <div class="w-full flex items-center">
      <Draggable
        :list="fieldSource"
		    :group="{ name: 'listOfFields', pull: true, put: false }"
        @change="log"
        drag-class="drag"
        ghost-class="ghost"
        item-key="fieldname"
      >
        <template #item="{ element }">
          <div class="p-3 mb-2 rounded cursor-pointer border-b-2">
            <h1 class="text-xl font-bold">
              {{ element.label }}
            </h1>
            <div class="flex">
              <h1>
                {{ element.fieldtype }}
              </h1>
              <h1 class="ml-2" v-if="element.fieldtype == 'Link'">
                - {{ element.options }}
              </h1>
            </div>
          </div>
        </template>
      </Draggable>
    </div>
  </div>
</template>

<script setup>
import Draggable from 'vuedraggable';
import { Button, TextInput, FeatherIcon } from 'frappe-ui'
const { fieldSource } = defineProps(['fieldSource'])
const log = function (evt) {
  window.console.log("Cloned", evt)
}
</script>
<style>
.ghost > template {
  background-color: gray;
  border-radius: 5px;
}
</style>
