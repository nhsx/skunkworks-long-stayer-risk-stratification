<template>
  <nhs-main>
    <nhs-grid-row>
      <nhs-grid-item>
      <nhs-heading caption="NHSX Long Stayer AI Risk Stratification Modelling">
          Patient Long Stay Prediction</nhs-heading>
        <p>
          This system produces a predictive Long-Term Stay Score (LTSS) based on patient
          admission data. A score is generated between 0 and 5, with 5 representing the
          highest risk of a patient being a long stayer.
        </p>
        <nhs-details summary="Background">
          Admission staff are the front line of triage, and are required to stratify patients
          into risk categories at various points through their treatment.  The ability to predict
          the risk of a patient becoming a long stayer, from the initial data provided at
          admission time, will allow for the preparation of care for the legitimate long-stayer,
          reducing the risk factors associated with such a long stay; as well as for
          identification of the initial risks of unnecessary long stays, leading to more positive
          outcomes for those patients.
        </nhs-details>
        <router-link :to="{ name: 'records' }">
          <nhs-button>View Demonstrator</nhs-button>
        </router-link>
      </nhs-grid-item>
    </nhs-grid-row>
  </nhs-main>
</template>

<script>
export default {
  name: 'Home',
};
</script>

<style scoped>

</style>
