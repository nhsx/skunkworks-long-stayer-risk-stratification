<template>
  <table :class="{
    'nhsuk-table': !responsive,
    'nhsuk-table-responsive': responsive,
    'table-interactive': interactive,
  }">
    <caption v-if="caption" class="nhsuk-table__caption">{{ caption }}</caption>
    <thead role="rowgroup" class="nhsuk-table__head">
      <tr role="row">
        <th v-for="h in columns" :key="h" role="columnheader" class="" scope="col">
          {{ h }}
        </th>
      </tr>
    </thead>
    <tbody class="nhsuk-table__body">
      <tr v-for="(row, idx) in data" :key="row" role="row" class="nhsuk-table__row"
        @click="$emit('rowSelect', idx)">
        <td v-for="(p, cellIdx) in zip(columns, row)"
            :key="`td-${idx}-${cellIdx}`" class="nhsuk-table__cell">
          <span v-if="responsive" class="nhsuk-table-responsive__heading">
            {{ p[0] }}
          </span>
          {{ p[1] }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
export default {
  name: 'nhs-table',
  props: {
    caption: {
      type: String,
      default: null,
    },
    responsive: {
      type: Boolean,
      default: false,
    },
    interactive: {
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
  },
};
</script>

<style lang="scss" scoped>
.table-interactive {
  tbody{
    tr:hover {
      background-color: #cce6ff;
    }
  }
}
</style>
