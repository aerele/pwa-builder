<template>
   <div class="p-2">
  <TextInput
    :type="'time'"
    size="sm"
    variant="subtle"
    :disabled="true"
    modelValue=""
  />
</div>
</template>
<script setup>
import { TextInput } from 'frappe-ui';
</script>