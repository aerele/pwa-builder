<template>
    <div class="p-2">
  <Select
    :options="[
      {
        label: 'John Doe',
        value: 'john-doe',
      },
      {
        label: 'Jane Doe',
        value: 'jane-doe',
      },
      {
        label: 'John Smith',
        value: 'john-smith',
      },
      {
        label: 'Jane Smith',
        value: 'jane-smith',
        disabled: true,
      },
      {
        label: 'John Wayne',
        value: 'john-wayne',
      },
      {
        label: 'Jane Wayne',
        value: 'jane-wayne',
      },
    ]"
    v-model="value"
  />
</div>
</template>
<script setup>
import { Select } from 'frappe-ui'
</script>