# NHSX-LTSS Demonstrator WebUI

The WebUI component is built on the [Vue.js 3](https://v3.vuejs.org/guide/introduction.html) framework and implements 
[NHS.UK frontend components](https://nhsuk.github.io/nhsuk-frontend/) (in line with the [NHS Digital Service design system](https://service-manual.nhs.uk/design-system/components)).

## NHS.UK frontend components

The NHS.UK Digital Service publish a suite of frontend user interface components that are designed to offer a consistent
and well-designed user experience when accessing NHS materials online. In order to rapidly prototype a WebUI that would
be familiar in look and feel, we have used these frontend components as the building blocks for this project. 

These components are distributed as a package that can be installed using the node package manager (npm). Installation
of the npm package make the html components available to import into the project. To make these html components available
for use in the Vue.js framework, we have built out a component library that wraps the base NHS.UK artefacts in vue directives.

For example, the NHS.UK Button component can be defined in plain HTML with:
```html
<button class="nhsuk-button nhsuk-button--secondary" type="submit">
  Save and continue
</button>
```
The equivalent vue component in our component library is defined with:
```vue
<nhs-button secondary>Save and continue</nhs-button>
```
Where components are configurable (such as the use of secondary button styling above), vue properties have been used to
apply the correct rendering of the components as per the NHS design system.

## Layout

The WebUI implementation is structured as follows:
* [package.json](package.json), [package-lock.json](package-lock.json) - Package details, NPM package requirements, Linter config
* [babel.config.js](babel.config.js) - Babel config presets
* [vue.config.js](vue.config.js) - Vue config for development endpoint and SCSS config
* [public](public) - Static assets including: icons, logos, base `index.html`
* [src](src)
  * [assets](src/assets) - Common elements: global styling, data field definitions
  * [components](src/components) - Vue.js compatible NHS.UK frontend components
  * [views](src/components) - Main WebUI page views
  * [App.vue](src/components) - Base Vue app view definition
  * [main.js](src/main.js) - Main js source to create Vue app
  * [router.js](src/router.js) - Routing definitions for page navigation  
  

