<template>
    <div class="p-2">
  <Checkbox
    size="sm"
    :value="false"
    v-model="state.value"
    label="Enable feature"
  />
</div>
</template>
<script setup>
import { TextInput } from 'frappe-ui';
</script>