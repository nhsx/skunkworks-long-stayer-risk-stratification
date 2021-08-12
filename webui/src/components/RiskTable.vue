<template>
  <table :class="{
    'nhsuk-table': !responsive,
    'nhsuk-table-responsive': responsive,
  }">
    <thead role="rowgroup" class="nhsuk-table__head">
      <tr role="row">
        <th v-for="h in columns" :key="h" role="columnheader" class="" scope="col">
          {{ h }}
        </th>
      </tr>
    </thead>
    <tbody class="nhsuk-table__body">
      <tr v-for="(row, idx) in data" :key="row" role="row" class="nhsuk-table__row">
        <td v-for="(p, cellIdx) in zip(columns, row)" role="cell"
            :key="`td-${idx}-${cellIdx}`" class="nhsuk-table__cell"
            :style="riskColour(p[1])">
          <span v-if="responsive" class="nhsuk-table-responsive__heading">
            {{ p[0] }}
          </span>
          {{ formatCell(p[1]) }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import ColourScheme from '@/assets/common';

export default {
  name: 'RiskTable',
  props: {
    responsive: {
      type: Boolean,
      default: false,
    },
    columns: {
      type: Array,
      required: true,
      default() { return []; },
    },
    data: {
      type: Array,
      default() { return []; },
    },
  },
  methods: {
    zip(a, b) {
      return a.map((k) => [k, b[k]]);
    },
    riskColour(risk) {
      if (risk < 1 || risk > 5) return { backgroundColour: '#fffff' };
      return { backgroundColor: ColourScheme.COLOURS[risk - 1] };
    },
    formatCell(cell) {
      if (typeof (cell) === 'number') { return cell; }
      return cell.split(' ')
        .map((w) => w[0].toUpperCase() + w.substr(1).toLowerCase())
        .join(' ');
    },
  },
};
</script>

<style lang="scss" scoped>
</style>
