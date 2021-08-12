<template>
  <dl :class="{ 'nhsuk-summary-list': true, 'nhsuk-summary-list--no-border': !border }">
    <slot></slot>
  </dl>
</template>

<script>
export default {
  name: 'nhs-summary-list',
  props: {
    border: {
      type: Boolean,
      default: true,
    },
  },
};
</script>

<style scoped>

</style>
