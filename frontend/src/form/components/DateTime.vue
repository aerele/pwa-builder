<template>
    <div class="p-2">
  <TextInput
    :type="'datetime-local'"
    size="sm"
    variant="subtle"
    placeholder="Placeholder"
    :disabled="false"
    modelValue=""
  />
</div>
</template>
<script setup>
import { TextInput } from 'frappe-ui';
</script>