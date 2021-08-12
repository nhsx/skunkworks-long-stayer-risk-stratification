<template>
    <nhs-header organisational organisation-name="Gloucestershire Hospitals"
                organisation-descriptor="NHS Foundation Trust"
                :skip-link=false>
      <template #content><img src="./assets/poly.svg" /></template>
    </nhs-header>
      <router-view />
</template>

<script>
export default {
  name: 'App',
};
</script>

<style lang="scss">
@import 'node_modules/nhsuk-frontend/packages/nhsuk';
@import 'assets/theme';
</style>
