<template>
  <div class="px-4">
    <div v-if="fieldSource" class="w-full py-6">
      <TextInput 
        v-model="searchQuery" 
        type="text" 
        placeholder="Search Here"
        @input="handleInput"
      >
        <template #prefix>
          <FeatherIcon class="w-4" name="search" />
        </template>
      </TextInput>
    </div>
    <div class="w-full items-center">
      <Draggable
        :list="fieldSource"
        :group="{ name: 'listOfFields', pull: true, put: false }"
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
import { ref } from 'vue';
import Draggable from 'vuedraggable';
import { Button, TextInput, FeatherIcon } from 'frappe-ui';

const { fieldSource } = defineProps(['fieldSource']);
const searchQuery = ref('');
const emit = defineEmits(['handle_field_search']);
const handleInput = () => {
  // console.log(searchQuery.value)
  emit('handle_field_search', searchQuery.value);
};

</script>

<style>
.ghost > template {
  background-color: gray;
  border-radius: 5px;
}
</style>
