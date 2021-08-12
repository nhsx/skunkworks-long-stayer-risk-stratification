<template>
  <div :class="{ 'nhsuk-form-group': true, 'nhsuk-form-group--error': error }">
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'nhs-form-group',
  props: {
    error: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<style scoped>

</style>
