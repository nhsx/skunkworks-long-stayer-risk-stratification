<template>
  <nhs-details class="nhsuk-expander" :summary="summary">
    <slot></slot>
  </nhs-details>
</template>

<script>
export default {
  name: 'nhs-expander',
  props: {
    summary: {
      type: String,
      default: 'Summary',
    },
  },
};
</script>

<style scoped>

</style>
