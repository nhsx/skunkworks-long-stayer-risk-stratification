<template>
  <div :class="`nhsuk-grid-column-${gridWidth}`">
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'nhs-grid-item',
  props: {
    gridWidth: {
      default: 'full',
      validator(v) {
        return ['full', 'one-half', 'two-thirds', 'one-third', 'three-quarters',
          'one-quarter'].indexOf(v) !== -1;
      },
    },
  },
};
</script>

<style scoped>

</style>
