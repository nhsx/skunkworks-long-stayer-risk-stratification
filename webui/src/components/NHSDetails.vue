<template>
  <details class="nhsuk-details">
    <summary class="nhsuk-details__summary">
      <span class="nhsuk-details__summary-text">
        {{ summary }}
      </span>
    </summary>
    <div class="nhsuk-details__text">
      <slot></slot>
    </div>
  </details>
</template>

<script>
export default {
  name: 'nhs-details',
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
