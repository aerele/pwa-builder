<template>
    <div class=" px-4">
    <div v-if="fieldSource" class="w-full py-6" placeholder="Search Here">
      <TextInput type="text" placeholder="Search Here">
        <template #prefix>
          <FeatherIcon class="w-4" name="search" />
        </template>
      </TextInput>
    </div>
    <div class="w-full items-center">
      <Draggable
        :list="fieldSource"
		    :group="{ name: 'listOfFields', pull: true, put: false }"
        @change="log"
        drag-class="drag"
        ghost-class="ghost"
        item-key="fieldname"
        :sort="false"
      >
        <template #item="{ element }">
          <div class="p-3 mb-2 rounded cursor-pointer border-b-2 hover:bg-gray-200 w-full">
            <h1 class="text-lg font-semibold">
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

