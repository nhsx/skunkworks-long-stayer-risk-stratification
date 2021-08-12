<template>
  <fieldset class="nhsuk-fieldset">
    <legend class="nhsuk-fieldset__legend nhsuk-fieldset__legend--l">
      <h1 class="nhsuk-fieldset__heading">
        {{ legend }}
      </h1>
    </legend>
    <slot></slot>
  </fieldset>
</template>

<script>
export default {
  name: 'nhs-fieldset',
  props: {
    legend: {
      type: String,
      default: null,
    },
  },
};
</script>

<style scoped>

</style>
