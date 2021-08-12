<template>
  <strong :class="`nhsuk-tag ${colourClass}`">
    <slot></slot>
  </strong>
</template>

<script>
export default {
  name: 'nhs-tag',
  props: {
    colour: {
      type: String,
      validator(v) {
        return ['white', 'grey', 'green', 'aqua-green', 'blue',
          'purple', 'pink', 'red', 'orange', 'yellow'].indexOf(v) !== -1;
      },
    },
  },
  computed: {
    colourClass() {
      return this.colour ? `nhsuk-tag--${this.colour}` : '';
    },
  },
};
</script>

<style scoped>

</style>
