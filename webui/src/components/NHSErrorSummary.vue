<template>
  <div class="nhsuk-error-summary" :aria-labelledby="`${id}--title`" role="alert" tabindex="-1">
    <h2 class="nhsuk-error-summary__title" :id="`${id}--title`">
      <span class="nhsuk-u-visually-hidden">Error:</span> {{ title }}
    </h2>
    <div class="nhsuk-error-summary__body">
      <slot></slot>
      <ul v-if="!!$slots.list" class="nhsuk-list nhsuk-error-summary__list">
        <slot name="list"></slot>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'nhs-error-summary',
  props: {
    id: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      default: 'There is a problem',
    },
  },
};
</script>

<style scoped>

</style>
