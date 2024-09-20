<template>
    <div class=" sm:w-full md:w-full lg:w-full xl:w-full w-screen">
        <div class="navbar h-15 border-b-2 flex items-center">
            <div class="flex flex-row justify-between w-full px-4">
                <div class="logo">
                    <!-- <img src="/assets/frappe/images/frappe-framework-logo.svg" alt="Logo"> -->
                </div>
                <!-- <div class="flex flex-row items-center gap-2"> -->
                    <Avatar
                    label="Aerele Technologies"
                    shape="square"
                    size="2xl"/>
                <!-- </div> -->
            </div>
        </div>
        <div class="content-page px-10">
            <div class="mt-4">
                <div class="">
                    Projects
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-7">
                    <div class="w-24 h-24 bg-gray-400 flex items-center justify-center mt-4 ml-5 add-icon" @click="open = true">
                        <FeatherIcon name="plus" class="w-15 h-15 text-white" />
                    </div>

                    <div v-if="response.length" v-for="project in response" :key="project.name" >
                        <router-link :to="{ name:'BuilderEdit', params : { id : project.name } }">
                            <div class="w-24 h-24 flex items-center justify-center my-7 ml-5 add-icon">
                                <div class="flex flex-col items-center">
                                    <Avatar
                                    :label="project.project_title"
                                    :image="project.project_logo"
                                    shape="square"
                                    class="w-24 h-24 mb-1"
                                    />
                                    <div>{{ project.project_title }}</div>
                                </div>
                            </div>
                        </router-link>
                    </div>
                </div>
            </div>
        </div>
        <!-- <div v-if="showDrawer"> -->
            <TransitionRoot as="template" :show="open">
      <Dialog class="relative z-10" @close="open = false">
        <TransitionChild as="template" enter="ease-in-out duration-500" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in-out duration-500" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>
        <div class="fixed inset-0 overflow-hidden">
          <div class="absolute inset-0 overflow-hidden">
            <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
              <TransitionChild as="template" enter="transform transition ease-in-out duration-500 sm:duration-700" enter-from="translate-x-full" enter-to="translate-x-0" leave="transform transition ease-in-out duration-500 sm:duration-700" leave-from="translate-x-0" leave-to="translate-x-full">
                <DialogPanel class="pointer-events-auto relative w-screen max-w-md">
                  <TransitionChild as="template" enter="ease-in-out duration-500" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in-out duration-500" leave-from="opacity-100" leave-to="opacity-0">
                    <div class="absolute left-0 top-0 -ml-8 flex pr-2 pt-4 sm:-ml-10 sm:pr-4">
                      <button type="button" class="relative rounded-md text-gray-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-white" @click="open = false">
                        <span class="absolute -inset-2.5" />
                        <span class="sr-only">Close panel</span>
                        <!-- <XMarkIcon class="h-6 w-6" aria-hidden="true" /> -->
                         <FeatherIcon name="x" class="w-5 h-5" />
                      </button>
                    </div>
                  </TransitionChild>
                  <div class="flex h-full flex-col overflow-y-scroll bg-white py-6 shadow-xl">
                    <div class="px-4 sm:px-6">
                      <DialogTitle class="text-base font-semibold leading-6 text-gray-900">Create Project</DialogTitle>
                    </div>
                    <div class="relative mt-6 flex-1 px-4 sm:px-6">
                        <!-- <span>Project Name</span> -->
                         <div class="mb-2">
                             <Input type="text" label="Project Title" v-model="project.project_title" />
                         </div>
                         <!-- <div class="mb-2">
                             <Input type="text" label="Sub Title" v-model="project.sub_title"/>
                         </div> -->
                         <div class="mb-2">
                             <Input type="text" label="Site URL" v-model="project.site_url"/>
                         </div>
                         <div class="mb-2">
                             <Input type="email" label="User ID" v-model="project.user_id"/>
                         </div>
                         <div class="mb-2">
                             <Input type="password" label="Password" v-model="project.password"/>
                         </div>
                         <div class="mb-4">
                            <FormControl
                        :type="'textarea'"
                        size="sm"
                        variant="subtle"
                        placeholder=""
                        :disabled="false"
                        label="Description"
                        v-model="project.description"
                        />
                         </div>
                         <div>
                             <!-- <Button type="submit" class="w-full px-4 py-2 text-white bg-gray-800 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                 Create
                             </Button> -->
                             <Button class="w-full" variant="solid" theme="gray" @click="createProject">
                                Create
                             </Button>
                        </div>
                    </div>
                  </div>
                </DialogPanel>
              </TransitionChild>
            </div>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
        <!-- </div> -->
    </div>
</template>
<script setup>
import { Avatar, FeatherIcon, Input, FormControl, Button } from 'frappe-ui'
import { createListResource, createResource } from 'frappe-ui';
import Drawer from './Drawer.vue';
import { reactive, ref } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import Project from './Project.vue';

const open = ref(false)
let response = ref([])

let project = reactive({
    project_title: "",
    site_url: "",
    user_id: "",
    password: "",
    description: "",
})

let pwaProject = createResource({
    url: "pwa_builder.api.add_site",
    params: {data: project},
    transform(data) {
        console.log(data)
		pwaProjectList.reload()
        return data
    }
})

function createProject() {
    pwaProject.reload()
    open.value = false;
}
const pwaProjectList = createListResource({
    doctype: "PWA-Project",
    fields: ['project_title', 'sub_title', 'site_url', 'user_id', "name", "project_logo"],
    transform(data) {
        console.log(data)
        let transformData = []
        data.map((item) => {
            transformData.push(item)
        })
        response.value = transformData
        return transformData
    }
})

pwaProjectList.reload()

// function createProject() {
//     pwaProject.insert.submit(project);
//     open.value = false;
// }
</script>
<style>
.add-icon {
    border: 0px solid;
    border-radius: 8px;
}
</style>