import { createListResource } from 'frappe-ui'

// Shared list of PWA projects for the current user. Backed by
// frappe.client.get_list on PWA-Project (respects the user's permissions).
export const projects = createListResource({
  doctype: 'PWA-Project',
  fields: [
    'name',
    'project_title',
    'sub_title',
    'site_url',
    'project_logo',
    'github_repository_url',
    'modified',
  ],
  orderBy: 'modified desc',
  pageLength: 99,
  auto: true,
})

// "2d ago" style relative time from a Frappe datetime string.
export function relativeTime(value) {
  if (!value) return ''
  const then = new Date(value.replace(' ', 'T'))
  const secs = Math.round((Date.now() - then.getTime()) / 1000)
  if (secs < 60) return 'just now'
  const mins = Math.round(secs / 60)
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.round(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.round(hrs / 24)
  if (days < 7) return `${days}d ago`
  const weeks = Math.round(days / 7)
  if (weeks < 5) return `${weeks}w ago`
  return then.toLocaleDateString()
}
