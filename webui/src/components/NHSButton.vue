<template>
  <button :class="{
      'nhsuk-button': true,
      'nhsuk-button--secondary': secondary,
      'nhsuk-button--reverse': reverse,
    }" type="submit">
    <slot></slot>
  </button>
</template>

<script>
export default {
  name: 'nhs-button',
  props: {
    secondary: Boolean,
    reverse: Boolean,
  },
};
</script>

<style scoped>

</style>
