<template>
  <nhs-hint v-if="hint">
    {{ hint }}
  </nhs-hint>
  <nhs-error-message v-if="error">
    {{ error }}
  </nhs-error-message>
  <input v-bind="$attrs" :class="`nhsuk-input ${widthClass} ${error ? 'nhsuk-input--error' : ''}`"
         type="text" :numeric="numeric" :pattern="numeric ? '[0-9]*' : undefined">
</template>

<script>
export default {
  name: 'nhs-text-input',
  props: {
    hint: {
      type: String,
      default: null,
    },
    error: {
      type: String,
      default: null,
    },
    numeric: {
      type: Boolean,
      default: undefined,
    },
    textWidth: {
      type: Number,
      default: null,
      validator(v) {
        return [20, 10, 5, 4, 3, 2].indexOf(v) !== -1;
      },
    },
    fluidWidth: {
      type: String,
      default: null,
      validator(v) {
        return ['full', 'three-quarters', 'two-thirds',
          'one-half', 'one-third', 'one-quarter'].indexOf(v) !== -1;
      },
    },
  },
  computed: {
    widthClass() {
      if (this.textWidth != null) {
        return `nhsuk-input--width-${this.textWidth}`;
      }
      if (this.fluidWidth != null) {
        return `nhsuk-u-width-${this.fluidWidth}`;
      }
      return '';
    },
  },
};
</script>

<style scoped>

</style>
