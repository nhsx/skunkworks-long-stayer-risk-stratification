<template>
  <div :class="{
    'nhsuk-card': true,
    'nhsuk-card--clickable': clickable,
  }">
    <div class="nhsuk-card__content">
      <img v-if="img" class="nhsuk-card__img" :src="img" :alt="imgAlt">
      <h3 v-if="$slots.heading" class="nhsuk-card__heading">
        <slot name="heading"></slot>
      </h3>
      <h2 v-if="headingLink" class="nhsuk-card__heading nhsuk-heading-m">
        <a class="nhsuk-card__link" :href="headingLink">{{ headingLinkText || headingLink }}</a>
      </h2>
      <p class="nhsuk-card__description"><slot></slot></p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'nhs-card',
  props: {
    clickable: {
      type: Boolean,
      default: false,
    },
    img: {
      type: String,
      default: null,
    },
    imgAlt: {
      type: String,
      default: '',
    },
    headingLink: {
      type: String,
      default: null,
    },
    headingLinkText: {
      type: String,
      default: null,
    },
  },
};
</script>

<style scoped>
p {
  white-space: pre-wrap;
}
</style>
