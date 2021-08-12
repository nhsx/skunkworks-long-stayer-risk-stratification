<template>
  <div class="nhsuk-warning-callout">
    <h3 class="nhsuk-warning-callout__label">
    <span role="text">
      <span class="nhsuk-u-visually-hidden">Important: </span>
      {{ heading }}
    </span>
    </h3>
    <p>
      <slot></slot>
    </p>
  </div>
</template>

<script>
export default {
  name: 'nhs-warning-callout',
  props: {
    heading: {
      type: String,
      default: null,
    },
  },
};
</script>

<style scoped>

</style>
