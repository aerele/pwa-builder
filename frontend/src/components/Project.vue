<template>
    <div class="w-24 h-24 flex items-center justify-center my-7 ml-5 add-icon">
        <div class="flex flex-col items-center">
            <!-- <img src="https://raw.githubusercontent.com/frappe/erpnext/develop/erpnext/public/images/erpnext-logo.png" class="w-full h-full mb-1" /> -->
             <Avatar 
             :label="props.title"
             :img="props.img"
             class="w-full h-full mb-1"/>
            <div>{{ props.title }}</div>
        </div>
    </div>
</template>
<script setup>
import { Avatar } from 'frappe-ui'
const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    img: {
        type: Image,
    }
})
</script>