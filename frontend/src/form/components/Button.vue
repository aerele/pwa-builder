<template>
    <div class="p-2">
        <Button
        :variant="'solid'"
        theme="gray"
        size="sm"
        label="Button"
        :loading="false"
        :loadingText="null"
        :disabled="false"
        :link="null"
      >
        Button
      </Button>
    </div>
</template>
<script setup>
import { TextInput } from 'frappe-ui';
</script>