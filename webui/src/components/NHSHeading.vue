<template>
  <h1 class="app-page-heading">
    <span v-if="hasCaption" class="nhsuk-caption-l">
      {{ caption }}
      <span class="nhsuk-u-visually-hidden"> - </span>
    </span>
    <slot></slot>
  </h1>
</template>

<script>
export default {
  name: 'nhs-heading',
  props: {
    caption: {
      type: String,
      default: null,
    },
  },
  computed: {
    hasCaption() {
      return !!this.caption;
    },
  },
};
</script>

<style scoped>

</style>
