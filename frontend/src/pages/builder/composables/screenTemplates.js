/* Screen templates: prefill a freshly created screen's field_list from the
 * doctype meta. Same serialization the builder saves, so export is unchanged. */
import { createResource } from 'frappe-ui'
import { usableField } from './useBuilderState'

export const SCREEN_TEMPLATES = [
  { id: 'essentials', label: 'Essentials', icon: 'check-circle', description: 'Required fields, ready to validate' },
  { id: 'full', label: 'Everything', icon: 'list', description: 'All fields from the doctype' },
  { id: 'blank', label: 'Blank', icon: 'square', description: 'Start from an empty screen' },
]

export async function applyScreenTemplate(projectId, screen, templateId) {
  if (templateId === 'blank') return false
  const meta = await createResource({ url: 'pwa_builder.api.get_meta' }).submit({
    doctype: screen.doctype_name,
    project: projectId,
  })
  let fields = (meta?.fields || []).filter(usableField)
  if (templateId === 'essentials') fields = fields.filter((f) => f.reqd)
  if (!fields.length) return false
  fields = JSON.parse(JSON.stringify(fields))
  fields.forEach((f, i) => (f.idx = i + 1))
  await createResource({ url: 'pwa_builder.api.set_value' }).submit({
    doctype: 'PWA DocType',
    docname: screen.name,
    fieldname: 'field_list',
    value: {
      form_name: screen.title,
      name: screen.name,
      doctype_name: screen.doctype_name,
      is_submittable: meta?.is_submittable || 0,
      pwa_form_fields: fields,
    },
  })
  return true
}
