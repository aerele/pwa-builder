<template>
  <AuthLayout
    title="Create your account"
    subtitle="Start building PWAs in minutes."
  >
    <form @submit.prevent="signUp" class="space-y-4">
      <FormControl
        required
        type="text"
        label="Full Name"
        v-model="fullName"
        placeholder="John Doe"
      >
        <template #prefix><FeatherIcon class="w-4" name="user" /></template>
      </FormControl>

      <FormControl
        required
        type="email"
        label="Email"
        v-model="email"
        placeholder="johndoe@email.com"
      >
        <template #prefix><FeatherIcon class="w-4" name="mail" /></template>
      </FormControl>

      <p v-if="formSubmitted && !emailValid" class="auth-error">
        Enter a valid email
      </p>

      <p
        v-if="message"
        class="auth-alert"
        :class="`auth-alert--${messageType}`"
      >
        {{ message }}
      </p>

      <button type="submit" class="btn-primary" :disabled="loading">
        {{ loading ? 'Creating…' : 'Sign Up' }}
      </button>
    </form>

    <template #footer>
      Already have an account?
      <router-link to="/login" class="auth-link">Back to login</router-link>
    </template>
  </AuthLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, FeatherIcon, createResource } from 'frappe-ui'
import AuthLayout from '@/components/AuthLayout.vue'

const fullName = ref('')
const email = ref('')
const message = ref('')
const messageType = ref('error')
const formSubmitted = ref(false)
const loading = ref(false)

const emailValid = computed(() => /\S+@\S+\.\S+/.test(email.value))

// Guests can't insert User; frappe's sign_up honours "Disable Signup" and emails a password link.
async function signUp() {
  formSubmitted.value = true
  message.value = ''
  if (!emailValid.value) return

  loading.value = true
  try {
    const [status, text] = await createResource({
      url: 'frappe.core.doctype.user.user.sign_up',
    }).submit({
      email: email.value,
      full_name: fullName.value,
      redirect_to: '/pwa-builder',
    })
    messageType.value = status ? 'ok' : 'error'
    message.value = text
  } catch (error) {
    messageType.value = 'error'
    message.value = error?.messages?.[0] || 'Could not create the account'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.btn-primary {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 600;
  color: var(--brand-fg);
  background: var(--brand);
  border-radius: var(--radius-control);
}
.btn-primary:hover:not(:disabled) {
  background: var(--brand-hover);
}
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.auth-link {
  color: var(--brand);
  font-weight: 500;
}
.auth-link:hover {
  text-decoration: underline;
}
.auth-error {
  margin-top: -8px;
  font-size: 12px;
  color: var(--danger);
}
.auth-alert {
  padding: 8px 12px;
  border-radius: var(--radius-control);
  font-size: 13px;
}
.auth-alert--error {
  color: var(--danger);
  background: rgba(220, 38, 38, 0.08);
}
.auth-alert--ok {
  color: var(--ok);
  background: rgba(22, 163, 74, 0.08);
}
</style>
