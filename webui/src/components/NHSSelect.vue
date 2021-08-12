<template>
  <select class="nhsuk-select"
  :value="modelValue"
  @change="$emit('update:modelValue', $event.target.value)">
    <slot></slot>
  </select>
</template>

<script>
export default {
  name: 'nhs-select',
  props: ['modelValue'],
};
</script>

<style scoped>

</style>
