<template>
  <div :class="containerClass">
    <main :class="mainClass" id="maincontent" role="main">
      <slot></slot>
    </main>
  </div>
</template>

<script>
export default {
  name: 'nhs-main',
  props: {
    fluid: {
      type: Boolean,
      default: false,
    },
    vLarge: {
      type: Boolean,
      default: false,
    },
    vSmall: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    containerClass() {
      return this.fluid ? 'nhsuk-width-container-fluid' : 'nhsuk-width-container';
    },
    mainClass() {
      if (this.vSmall) {
        return 'nhsuk-main-wrapper--s';
      }
      if (this.vLarge) {
        return 'nhsuk-main-wrapper--l';
      }
      return 'nhsuk-main-wrapper';
    },
  },
};
</script>

<style scoped>

</style>
