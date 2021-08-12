<template>
  <nhs-main class="forecast-page">
    <nhs-grid-row>
      <nhs-grid-item>
        <nhs-back-link href="#/records"></nhs-back-link>
        <nhs-heading caption="NHSX Long Stayer AI Risk Stratification Modelling">
          Patient Forecast</nhs-heading>
        <h2><i class="icon-person" /> Patient Record #{{ patientId }}</h2>
        <nhs-warning-callout v-if="recordManipulated" heading="Explorative Forecast">
          This forecast is based on edited patient data,
          to retrieve the original patient record and forecast select
          'Reset Record'.
        </nhs-warning-callout>
        <div class="loading-spinner" v-if="!isError && isLoading">
          <loading v-model:active="isLoading"
                   :can-cancel="false"
                   :is-full-page="true"
                   color="#005eb8"
                   :width="128" :height="128"
          />
        </div>
        <div v-else-if="patientRecord && !isError && !isLoading">
          <nhs-grid-row>
            <nhs-grid-item gridWidth="one-half"> <!-- Left Block - Patient Record -->
              <nhs-card>
                <nhs-button class="forecastButton" @click="resetFields">Reset Record</nhs-button>
                <nhs-button class="forecastButton" secondary
                            @click="getEditedForecast">Generate New Forecast</nhs-button>
                <nhs-summary-list v-for="(group, idx) in editedRecord" :key="idx">
                  <h3><i class="icon-menu"/> {{ recordSections[idx] }}</h3>
                  <nhs-summary-list-row v-for="(value, name) in group"
                                        :key="name" :title="toTitleCase(name)">
                    <p class="capitalise" v-if="!editable(name)">
                      {{ textDescriptor(name, value) }}
                    </p>
                    <nhs-select class="capitalise" v-else v-model="editedRecord[idx][name]">
                      <option v-for="(option, idy) in VariableFields[name]"
                          :value="option" :key="idy">
                        {{ textDescriptor(name, option) }}
                      </option>
                    </nhs-select>
                  </nhs-summary-list-row>
                </nhs-summary-list>
              </nhs-card>
            </nhs-grid-item> <!-- End Left Block -->
            <nhs-grid-item gridWidth="one-half">
              <nhs-grid-row v-if="patientForecast">
                <nhs-grid-item> <!-- Right Block - Predictions -->
                  <nhs-card>
                    <h3>The risk stratification score is currently at:</h3>
                    <nhs-card class="result-card" :style=riskColour>
                      <template #heading>{{ riskText }}</template>
                    </nhs-card>
                    <h3>This patient has a {{ patientForecast.PERCENTAGE_RISK_CAT }}% chance
                    of becoming a long stayer</h3>
                  </nhs-card>
                  <nhs-card>
                    <h3>The AI model predicts this patient will stay for:</h3>
                    <nhs-card class="result-card los-card">
                      <template #heading>{{ losText }}</template>
                    </nhs-card>
                    <h3>The patient should be medically optimised after:</h3>
                    <nhs-card class="result-card mot-card">
                      <template #heading>{{ motText }}</template>
                      If they stay for longer than this they are considered to be at risk
                    </nhs-card>
                  </nhs-card>
                </nhs-grid-item> <!-- End Predictions -->
                <nhs-grid-item> <!-- Right Block - Visuals -->
                  <nhs-card>
                    <nhs-expander summary="Risk Level Likelihood Chart">
                      <h3>Length of Stay<br />Risk Level Likelihoods</h3>
                      <p-d-chart
                          :chartData="chartDataset()"
                          :chartOptions="{
                            responsive:true,
                            legend:{display:false},
                            scales: {
                              xAxes: [{
                                scaleLabel: {
                                  display: true,
                                  labelString: 'Likelihood %',
                                  fontSize: 18,
                                }
                              }],
                              yAxes : [{
                                scaleLabel: {
                                  display: true,
                                  labelString: 'LoS Risk Level',
                                  fontSize: 14,
                                }
                              }],
                            }}" />
                    </nhs-expander>
                    <nhs-expander summary="Risk Level Per Category">
                      <risk-table responsive
                                  :columns="['Risk Factors', 'Risk']"
                                  :data="riskFactors"
                      />
                    </nhs-expander>
                  </nhs-card>
                </nhs-grid-item> <!-- End Visuals -->
              </nhs-grid-row>
              <nhs-grid-row v-else>
                <nhs-grid-item gridWidth="full">
                  <nhs-warning-callout heading="No Forecast Available">
                    No forecast is available for this record. This may be due
                    to the record fields being outside the scope of the predictive model
                    or simply due to an error retrieving the data.
                  </nhs-warning-callout>
                </nhs-grid-item>
              </nhs-grid-row>
            </nhs-grid-item>
          </nhs-grid-row>
        </div>
        <nhs-error-summary v-else id="error" title="Error loading patient record">
          <template v-slot:list>
            <li>
              <a href="#/records">
                Refresh the current page or click here to return to the previous page
              </a>
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
import PDChart from '@/components/PDChart.vue';
import RiskTable from '@/components/RiskTable.vue';

import ColourScheme from '@/assets/common';
import { CategoryLookup, VariableFields } from '@/assets/data';
import Utils from '@/util';

export default {
  name: 'Forecast',
  components: {
    PDChart,
    Loading,
    RiskTable,
  },
  props: {
    patientId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isLoading: false,
      isError: false,
      patientRecord: null,
      patientForecast: null,
      editedRecord: null,
      recordManipulated: false,
      recordSections: [
        'Personal',
        'Admission',
        'Medical',
        'Medical Coding',
        'Administrative',
        'Socio-Demographic',
      ],
      VariableFields,
    };
  },
  methods: {
    toTitleCase: Utils.toTitleCase,
    getForecast() {
      return axios.post('/api/forecast', this.editedRecord, {
        headers: { 'Content-Type': 'application/json' },
      })
        .then((response) => {
          if (response.data.forecast) {
            this.patientForecast = response.data.results;
          } else {
            this.patientForecast = null;
          }
        })
        .catch((err) => {
          console.error(err);
          this.patientForecast = null;
          this.isError = true;
          this.isLoading = false;
        });
    },
    getRecord() {
      return axios.get(`/api/record/${this.patientId}`)
        .then((response) => {
          this.patientRecord = response.data;
          this.editedRecord = JSON.parse(JSON.stringify(this.patientRecord));
        });
    },
    loadContents() {
      this.isLoading = true;
      this.getRecord()
        .then(() => {
          this.getForecast()
            .then(() => {
              setTimeout(() => {
                this.isLoading = false;
              }, 100);
            });
        })
        .catch((err) => {
          console.error(err);
          this.isError = true;
          this.isLoading = false;
        });
    },
    getEditedForecast() {
      this.getForecast()
        .then(() => {
          this.recordManipulated = true;
        })
        .catch((err) => {
          console.error(err);
          this.isError = true;
          this.isLoading = false;
        });
    },
    resetFields() {
      this.editedRecord = JSON.parse(JSON.stringify(this.patientRecord));
      this.getForecast()
        .then(() => {
          this.recordManipulated = false;
        })
        .catch((err) => {
          console.error(err);
          this.isError = true;
          this.isLoading = false;
        });
    },
    decToPercent(decimal) {
      return parseFloat(decimal) * 100;
    },
    chartDataset() {
      const scores = [
        this.decToPercent(this.patientForecast.RISK_CAT_PROB_GENERAL_1),
        this.decToPercent(this.patientForecast.RISK_CAT_PROB_GENERAL_2),
        this.decToPercent(this.patientForecast.RISK_CAT_PROB_GENERAL_3),
        this.decToPercent(this.patientForecast.RISK_CAT_PROB_GENERAL_4),
        this.decToPercent(this.patientForecast.RISK_CAT_PROB_GENERAL_5),
      ];
      return {
        datasets: [
          {
            data: scores,
            backgroundColor: ColourScheme.COLOURS,
            borderColor: ColourScheme.BORDERS,
            borderWidth: 1,
          },
        ],
        labels: ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
      };
    },
    editable(field) {
      return field in VariableFields;
    },
    textDescriptor(field, value) {
      if (field in CategoryLookup) {
        const typedValue = (typeof value === 'number') ? parseInt(value, 10) : value;
        if (typedValue in CategoryLookup[field]) {
          return CategoryLookup[field][typedValue];
        }
        return '';
      }
      if (value === 'null') return '';
      return value;
    },
  },
  created() {
    this.loadContents();
  },
  computed: {
    riskText() {
      return `Level ${this.patientForecast.RISK_STRATIFICATION}`;
    },
    riskColour() {
      const level = parseInt(this.patientForecast.RISK_STRATIFICATION, 10) - 1;
      return {
        backgroundColor: ColourScheme.COLOURS[level],
        borderColor: ColourScheme.BORDERS[level],
      };
    },
    motText() {
      const days = parseFloat(this.patientForecast.MOT_DAYS);
      const suffix = days > 1.0 || days === 0.0 ? 'days' : 'day';
      return `${days.toFixed()} ${suffix}`;
    },
    losText() {
      const days = parseFloat(this.patientForecast.PREDICTED_LOS);
      const suffix = days > 1.0 || days === 0.0 ? 'days' : 'day';
      return `${days.toFixed()} ${suffix}`;
    },
    riskFactors() {
      const factors = this.patientForecast.RISK_BY_CATEGORY;
      return Object.keys(factors)
        .map((k) => ({
          'Risk Factors': k.replace(/_/g, ' '),
          Risk: factors[k],
        }));
    },
  },
};
</script>

<style lang="scss" scoped>
.forecast-page {
  max-width: 65%;
}
.main-grid {
  text-align: center;
}
.loading-spinner {
  text-align: center;
}
.capitalise {
  text-transform: capitalize;
}
.result-card {
  text-align: center;
  margin-bottom: 20px;
}
.result-card-text {
  margin: 0;
}
.mot-card {
  background-color: #B4A7D6;
  border-color: #503B8B;
}
.los-card {
  background-color: #99ceff;
  border-color: #004f99;
}
.forecastButton {
  margin-left: 10px;
  margin-right: 10px;
}

</style>
