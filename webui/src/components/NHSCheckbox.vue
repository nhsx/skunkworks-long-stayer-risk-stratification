<template>
  <div class="nhsuk-checkboxes__item">
    <input :id="id" :name="id"
           class="nhsuk-checkboxes__input"
           type="checkbox" value="on"
           :checked="checked"
           @input="updateState">
    <label class="nhsuk-label nhsuk-checkboxes__label" :for="id">
      <slot></slot>
    </label>
    <nhs-hint v-if="hint" class="nhsuk-checkboxes__hint">
      {{ hint }}
    </nhs-hint>
  </div>
</template>

<script>
export default {
  name: 'nhs-checkbox',
  props: {
    id: {
      type: String,
      required: true,
    },
    checked: {
      type: Boolean,
      default: false,
    },
    hint: {
      type: String,
      default: undefined,
    },
  },
  methods: {
    updateState(e) {
      this.$emit('update:checked', e.target.checked);
    },
  },
};
</script>

<style scoped>

</style>
