<template>
    <div class="p-2">
  <FormControl
    :type="'textarea'"
    size="sm"
    variant="subtle"
    :disabled="true"
    v-model="inputValue"
  />
</div>
</template>
<script setup>
import { FormControl } from 'frappe-ui';
</script>