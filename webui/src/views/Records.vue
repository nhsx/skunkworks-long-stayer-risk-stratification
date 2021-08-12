<template>
  <nhs-main class="records-page">
    <nhs-grid-row>
      <nhs-grid-item>
        <nhs-warning-callout heading="Proof of Concept Demonstrator">
          This page is a placeholder for patient records in an existing EPRS.
          It exists for demonstration purposes and is not intended to replicate EPRS
          functionality.
        </nhs-warning-callout>
        <nhs-back-link></nhs-back-link>
        <nhs-heading caption="NHSX Long Stayer AI Risk Stratification Modelling">
          Patient Records
          <nhs-button @click="loadRecords">Reload</nhs-button>
        </nhs-heading>
        <div class="loading-spinner" v-if="isLoading && !isError">
          <loading v-model:active="isLoading"
                   :can-cancel="false"
                   :is-full-page="true"
                   color="#005eb8"
                   :width="128" :height="128"
          />
        </div>
        <nhs-table v-else-if="!isLoading && !isError"
            :columns="getRecordColumns"
            :data="getRecordRows"
            @rowSelect="navToForecast"
            interactive>
        </nhs-table>
        <nhs-error-summary v-else id="error" title="Error loading patient records">
          <template v-slot:list>
            <li>
              <a href="#/">Refresh the current page or click here to return to the previous page</a>
            </li>
          </template>
        </nhs-error-summary>
      </nhs-grid-item>
    </nhs-grid-row>
  </nhs-main>
</template>

<script>
import axios from 'axios';
import Loading from 'vue-loading-overlay';

import { CategoryLookup } from '@/assets/data';
import Utils from '@/util';

export default {
  name: 'Records',
  components: {
    Loading,
  },
  data() {
    return {
      isError: false,
      isLoading: false,
      records: {},
      summaryColumns: [
        'LOCAL_PATIENT_IDENTIFIER',
        'PATIENT_GENDER_CURRENT',
        'AGE_ON_ADMISSION',
        'PATIENT_CLASSIFICATION',
        'ETHNIC_CATEGORY_CODE_DESCRIPTION',
        'ADMISSION_METHOD_HOSPITAL_PROVIDER_SPELL_DESCRIPTION',
        'AE_ARRIVAL_MODE',
      ],
    };
  },
  methods: {
    loadRecords() {
      this.isLoading = true;
      this.isError = false;
      axios.get('/api/records')
        .then((response) => {
          this.records = response.data;
          this.isError = false;
          setTimeout(() => {
            this.isLoading = false;
          }, 100);
        })
        .catch((error) => {
          console.error(error);
          this.isError = true;
          this.isLoading = false;
        });
    },
    navToForecast(recordNumber) {
      this.$router.push({ name: 'forecast', params: { patientId: recordNumber } });
    },
  },
  computed: {
    getRecordColumns() {
      if (this.records && Object.keys(this.records).length > 0) {
        return this.summaryColumns
          .filter((item) => item in Object.values(this.records)[0])
          .map((item) => Utils.toTitleCase(item));
      }
      return [];
    },
    getRecordRows() {
      if (this.records && Object.keys(this.records).length > 0) {
        return Object.values(this.records).map((e) => {
          const result = {};
          this.summaryColumns.forEach((key) => {
            if (key in e) {
              if (key in CategoryLookup) {
                result[Utils.toTitleCase(key)] =
                    Utils.toTitleCase(CategoryLookup[key][parseInt(e[key], 10)]);
              } else {
                result[Utils.toTitleCase(key)] = Utils.toTitleCase(e[key]);
              }
            }
          });
          return result;
        });
      }
      return [];
    },
  },
  created() {
    this.loadRecords();
  },
};
</script>

<style lang="scss" scoped>
.records-page{
  max-width: 75%;
}
.loading-spinner {
  text-align: center;
}
</style>
