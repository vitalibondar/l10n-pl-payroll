# TASK-027 Tooltip Research

## Sources

- Odoo developer docs, `View architectures`, SaaS 18.4: field attribute `help` is documented as help tooltip displayed for the field label.
- Odoo Studio docs, 18.0: field properties include `Help Tooltip`.
- Odoo developer docs for `page` and layout elements: documented attributes cover `string`, `invisible`, etc., but not `help`.

Sources reviewed on 2026-03-29:

- https://www.odoo.com/documentation/saas-18.4/developer/reference/user_interface/view_architectures.html
- https://www.odoo.com/documentation/18.0/applications/studio/fields.html

## Findings

### 1. `help=` is the official tooltip mechanism for fields

Official Odoo docs explicitly define field attribute `help` as the help tooltip shown next to the field label. Studio exposes the same mechanism in the UI, which confirms that `help=` is the supported path for explainers aimed at non-experts.

### 2. Form views: supported

This is the main supported use case. If a field is rendered with its label in a form view, `help=` is the right way to attach an explanation.

### 3. List views: not reliably documented

The official documentation does not clearly promise list-view tooltip behavior for column headers. The docs describe `help` in terms of the field label, but they do not document a dedicated list-header tooltip UX. Practical recommendation: treat list-view help as undocumented and non-essential. Put the explanation on the form field.

This point is an inference from the docs, not an explicit guarantee from Odoo.

### 4. Notebook page headers: no native `help=`

`<page>` elements do not document a `help` attribute in Odoo view architecture docs. That means notebook tabs can have `string=`, invisibility rules, and related layout behavior, but not a built-in tooltip channel like model fields.

### 5. Group headers: same limitation

`<group>` is a layout container, not a field. Odoo docs do not document a native `help` tooltip for group headers either.

### 6. Practical workaround

If a section heading needs explanation:

- keep the section title short and professional
- attach `help=` to the first relevant fields inside the section
- if needed, add a short readonly informational field or warning block inside the page instead of trying to tooltip the page/group header

## Recommendation for This Module

- Add `help=` to payroll-specific fields on contract, employee, payslip, and wizard models.
- Do not rely on notebook page or group header tooltips; Odoo does not document them as supported.
- Use page/group titles only for accountant-friendly structure.
- Use field tooltips to explain Polish payroll concepts to non-experts.
