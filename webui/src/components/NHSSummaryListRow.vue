<template>
  <div class="nhsuk-summary-list__row">
    <dt class="nhsuk-summary-list__key">
      {{ title }}
    </dt>

    <dd class="nhsuk-summary-list__value">
      <slot></slot>
    </dd>

    <dd class="nhsuk-summary-list__actions" v-if="hasActions">
      <slot name="actions"></slot>
    </dd>
  </div>
</template>

<script>
export default {
  name: 'nhs-summary-list-row',
  props: {
    title: {
      type: String,
      required: true,
    },
  },
  computed: {
    hasActions() {
      return this.$slots.actions;
    },
  },
};
</script>

<style scoped>

</style>
