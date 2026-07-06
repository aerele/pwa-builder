import { computed, reactive } from 'vue'
import { createResource } from 'frappe-ui'

import { userResource } from './user'

export function sessionUser() {
  const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  let _sessionUser = cookies.get('user_id')
  if (_sessionUser === 'Guest') {
    _sessionUser = null
  }
  return _sessionUser
}

export const session = reactive({
  login: createResource({
    url: 'login',
    makeParams({ email, password }) {
      return {
        usr: email,
        pwd: password,
      }
    },
    onSuccess() {
      session.user = sessionUser()
      session.login.reset()
      // Full reload so the page re-renders with the authenticated session's
      // CSRF token (window.csrf_token). Without this, the first POST after an
      // in-page login fails CSRF validation ("Invalid Request").
      window.location.href = '/pwa-builder/'
    },
  }),
  logout: createResource({
    url: 'logout',
    onSuccess() {
      session.user = sessionUser()
      // Full reload to drop all in-memory state and refresh the token.
      window.location.href = '/pwa-builder/login'
    },
  }),
  user: sessionUser(),
  isLoggedIn: computed(() => !!session.user),
})
