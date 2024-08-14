<template>
    <div class="p-2">
        <Autocomplete
        :options="field.options"
        v-model="field.value"
        size="sm"
        variant="subtle"
        :label="field.label"
        :placeholder="field.label"
        :disabled="field.read_only"
        />
    </div>
</template>
<script>
import { Autocomplete } from 'frappe-ui'
</script>