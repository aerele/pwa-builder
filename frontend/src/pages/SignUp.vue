<template>
    <div class="min-h-screen bg-[#f4f5f7] flex justify-center items-center">
      <div class="w-full max-w-lg sm:w-96 bg-white rounded-lg p-6 shadow-md">
        <div class="w-full flex justify-center mb-4">
          <img :src="imageSrc" class="w-16 h-16 object-cover rounded-lg" />
        </div>
        <div class="text-center mb-4">
          <p class="font-medium text-xl">Sign Up</p>
        </div>
        <div>
          <FormControl
            required
            type="text"
            label="Username"
            name="username"
            v-model="username"
            placeholder="johndoe"
            class="mb-4"
          >
            <template #prefix>
              <FeatherIcon class="w-4" name="user" />
            </template>
          </FormControl>
          <FormControl
            required
            type="email"
            label="Email"
            name="email"
            v-model="email"
            placeholder="johndoe@email.com"
            class="mb-4"
          >
            <template #prefix>
              <FeatherIcon class="w-4" name="mail" />
            </template>
          </FormControl>
          <div class="relative mb-4">
            <FormControl
              required
              label="Password"
              name="password"
              v-model="password"
              :type="passwordFieldType"
              placeholder="••••••"
              class="w-full"
            >
              <template #prefix>
                <FeatherIcon class="w-4" name="lock" />
              </template>
            </FormControl>
            <span
              @click="togglePasswordVisibility"
              class="absolute right-2 top-5 cursor-pointer text-gray-600 text-sm p-2"
            >
              {{ passwordToggleText }}
            </span>
          </div>
          <div class="relative mb-4">
            <FormControl
              required
              label="Confirm Password"
              name="confirmPassword"
              v-model="confirmPassword"
              :type="confirmPasswordFieldType"
              placeholder="••••••"
              class="w-full"
            >
              <template #prefix>
                <FeatherIcon class="w-4" name="lock" />
              </template>
            </FormControl>
            <span
              @click="toggleConfirmPasswordVisibility"
              class="absolute right-2 top-5 cursor-pointer text-gray-600 text-sm p-2"
            >
              {{ confirmPasswordToggleText }}
            </span>
          </div>
          <div v-if="formSubmitted && !emailValid" class="text-red-500 text-xs mb-4">
            Enter a valid email!
          </div>
          <div v-if="formSubmitted && !passwordsMatch" class="text-red-500 text-xs mb-4">
            Passwords do not match!
          </div>
          <div>
            <Button
              :loading="loading"
              variant="solid"
              class="w-full mb-4"
              @click="signUp"
            >
              Sign Up
            </Button>
          </div>
          <div class="text-center">
            <router-link
              to="/login"
              class="text-sm font-medium text-black hover:underline"
            >
              Back to Login
            </router-link>
          </div>
        </div>
      </div>
      <div class="fixed bottom-0 w-full max-w-lg sm:w-96 p-3">
        <transition name="fade">
          <div
            v-if="responseMessage"
            class="w-full p-2 text-sm leading-5 text-white bg-blue-500 rounded-lg opacity-100 animate-slide-in-right animate-fade-out"
          >
            {{ responseMessage }}
          </div>
        </transition>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import { FormControl, Button, FeatherIcon, createListResource } from 'frappe-ui'
  
  const imageSrc = ref('')
  const username = ref('')
  const email = ref('')
  const password = ref('')
  const confirmPassword = ref('')
  const responseMessage = ref('')
  const formSubmitted = ref(false)
  const loading = ref(false)
  
  const showPassword = ref(false)
  const showConfirmPassword = ref(false)
  
  const emailValid = computed(() => /\S+@\S+\.\S+/.test(email.value))
  const passwordsMatch = computed(() => password.value === confirmPassword.value)
  
  const passwordFieldType = computed(() => showPassword.value ? 'text' : 'password')
  const confirmPasswordFieldType = computed(() => showConfirmPassword.value ? 'text' : 'password')
  const passwordToggleText = computed(() => showPassword.value ? 'Hide' : 'Show')
  const confirmPasswordToggleText = computed(() => showConfirmPassword.value ? 'Hide' : 'Show')
  
  const togglePasswordVisibility = () => {
    showPassword.value = !showPassword.value
  }
  
  const toggleConfirmPasswordVisibility = () => {
    showConfirmPassword.value = !showConfirmPassword.value
  }
  
  const currentURL = ref(window.location.href)
  const baseURL = computed(() => {
    const url = new URL(currentURL.value)
    return `${url.protocol}//${url.hostname}:8003`
  })
  const modifiedLogoURL = ref(`${baseURL.value}/assets`)
  
  const fetchLogo = () => {
    const myHeaders = new Headers()
    myHeaders.append('Cookie', 'full_name=Guest; sid=Guest; system_user=no; user_id=Guest; user_image=')
  
    const requestOptions = {
      method: 'GET',
      headers: myHeaders,
      redirect: 'follow',
    }
  
    fetch(modifiedLogoURL.value, requestOptions)
      .then((response) => response.text())
      .then((result) => {
        const parser = new DOMParser()
        const doc = parser.parseFromString(result, 'text/html')
        const link = doc.querySelector('link[rel="shortcut icon"]')
        if (link) {
          imageSrc.value = link.href
        }
      })
      .catch((error) => console.error(error))
  }
  
  const signUp = () => {
    loading.value = true
    formSubmitted.value = true
  
    const NewUser = createListResource({
      doctype: 'User',
    })
  
    NewUser.insert
      .submit({
        email: email.value,
        first_name: username.value,
        new_password: password.value,
      })
      .then(() => {
        responseMessage.value = 'User Created successfully'
        loading.value = false
      })
      .catch((error) => {
        if (error.response && error.response.status === 417) {
          responseMessage.value = 'Password is too weak'
        } else if (error.response && error.response.status === 409) {
          responseMessage.value = 'Email already exists'
        } else {
          console.error('Error creating user:', error)
          responseMessage.value = 'Error creating User'
        }
        loading.value = false
      })
  }
  
  fetchLogo()
  </script>
  
  <style scoped>
  @media (min-width: 640px) {
    .sm\:w-96 {
      width: 24rem;
    }
  }
  
  @media (max-width: 640px) {
    .sm\:w-96 {
      width: 100%;
    }
  }
  </style>
  