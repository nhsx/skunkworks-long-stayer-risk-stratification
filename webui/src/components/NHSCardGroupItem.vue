<template>
  <li :class="`nhsuk-grid-column-${gridWidth} nhsuk-card-group__item`">
    <slot></slot>
  </li>
</template>

<script>
export default {
  name: 'nhs-card-group-item',
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
