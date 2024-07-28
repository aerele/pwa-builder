<template>
  <div class="h-screen">
    <div class="">
      <h1>Nav Bar</h1>
    </div>
    <div class="grid grid-cols-12 gap-4 h-full">
      <div class="col-span-3">
        <FormList />
      </div>
      <div class="col-span-6">
        <BuilderCanvas :fieldList="fieldList"/>
      </div>
      <div class="col-span-3">
        <FieldList :fieldSource="fields.pwa_form_fields" />
      </div>
    </div>
  </div>
</template>

<script setup>
import FormList from './components/FormList.vue'
import BuilderCanvas from './components/BuilderCanvas.vue'
import FieldList from './components/FieldList.vue'
import { ref } from 'vue'

let fieldList = ref([
  {
    fieldname: 'basic_info',
    fieldtype: 'Section Break',
    label: 'Name and Type',
    oldfieldtype: 'Section Break',
    options: 'fa fa-user',
  },
  {
    bold: 1,
    fieldname: 'customer_name',
    fieldtype: 'Data',
    in_global_search: 1,
    label: 'Full Name',
    no_copy: 1,
    oldfieldname: 'customer_name',
    oldfieldtype: 'Data',
    reqd: 1,
    search_index: 1,
  },
  {
    fieldname: 'date',
    fieldtype: 'Date',
    label: 'Date',
  },
])

const fields = {
  pwa_form_fields: [
    {
      fieldname: 'basic_info',
      fieldtype: 'Section Break',
      label: 'Name and Type',
      oldfieldtype: 'Section Break',
      options: 'fa fa-user',
    },
    {
      bold: 1,
      fieldname: 'customer_name',
      fieldtype: 'Data',
      in_global_search: 1,
      label: 'Full Name',
      no_copy: 1,
      oldfieldname: 'customer_name',
      oldfieldtype: 'Data',
      reqd: 1,
      search_index: 1,
    },
    {
      fieldname: 'date',
      fieldtype: 'Date',
      label: 'Date',
    },
    {
      fieldname: 'datetime',
      fieldtype: 'Datetime',
      label: 'Datetime',
    },
    {
      default: 'Company',
      fieldname: 'customer_type',
      fieldtype: 'Select',
      label: 'Type',
      oldfieldname: 'customer_type',
      oldfieldtype: 'Select',
      options: 'Company\nIndividual',
      reqd: 1,
    },
    {
      default: '0',
      fieldname: 'disabled',
      fieldtype: 'Check',
      label: 'Disabled',
    },
    {
      fieldname: 'outstanding_amount',
      fieldtype: 'Currency',
      label: 'Outstanding Amount',
      options: 'currency',
    },
    {
      description: 'Select, to make the customer searchable with these fields',
      fieldname: 'primary_address_and_contact_detail',
      fieldtype: 'Section Break',
      label: 'Primary Address and Contact Detail',
    },
    {
      fieldname: 'primary_address',
      fieldtype: 'Text',
      label: 'Primary Address',
    },
    {
      fieldname: 'secondary_address',
      fieldtype: 'Long Text',
      label: 'Secondary Address',
    },
    {
      fieldname: 'secondary_address_1',
      fieldtype: 'Long Text',
      label: 'Secondary Address 1',
    },
    {
      fieldname: 'secondary_address_2',
      fieldtype: 'Text Editor',
      label: 'Secondary Address 2',
    },
    {
      collapsible: 1,
      fieldname: 'default_receivable_accounts',
      fieldtype: 'Section Break',
      label: 'Accounting',
    },
    {
      collapsible: 1,
      fieldname: 'credit_limit_section',
      fieldtype: 'Section Break',
      label: 'Credit Limit and Payment Terms',
    },
    {
      collapsible: 1,
      collapsible_depends_on: 'customer_details',
      fieldname: 'more_info',
      fieldtype: 'Section Break',
      label: 'More Information',
      oldfieldtype: 'Section Break',
      options: 'fa fa-file-text',
    },
    {
      description: 'Additional information regarding the customer.',
      fieldname: 'customer_details',
      fieldtype: 'Small Text',
      label: 'Customer Details',
    },
    {
      fieldname: 'column_break_45',
      fieldtype: 'Column Break',
      label: 'Column Break',
    },
    {
      fieldname: 'market_segment',
      fieldtype: 'Link',
      label: 'Market Segment',
      options: 'Market Segment',
    },
    {
      collapsible: 1,
      collapsible_depends_on: 'default_sales_partner',
      fieldname: 'sales_team_section_break',
      fieldtype: 'Section Break',
      label: 'Sales Partner and Commission',
      oldfieldtype: 'Section Break',
      options: 'fa fa-group',
    },
    {
      fieldname: 'default_commission_rate',
      fieldtype: 'Float',
      label: 'Commission Rate',
      oldfieldname: 'default_commission_rate',
      oldfieldtype: 'Currency',
    },
    {
      collapsible: 1,
      collapsible_depends_on: 'sales_team',
      fieldname: 'sales_team_section',
      fieldtype: 'Section Break',
      label: 'Sales Team',
    },
    {
      default: '0',
      fieldname: 'credit_limits',
      fieldtype: 'Int',
      label: 'Credit Limit',
    },
    {
      fieldname: 'country',
      fieldtype: 'Autocomplete',
      label: 'Country',
    },
  ],
  form_name: 'Test Form',
  doctype_name: 'Customer',
  name: 'cus_customer.json',
  is_submittable: 0,
  is_child_table: 0,
  parent_form: 0,
}
</script>
