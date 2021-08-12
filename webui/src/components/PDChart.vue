<script>
import { HorizontalBar } from 'vue3-chart-v2';

export default {
  name: 'PDChart',
  extends: HorizontalBar,
  props: {
    chartData: {
      type: Object,
      required: true,
    },
    chartOptions: {
      type: Object,
      required: true,
    },
  },
  mounted() {
    this.renderChart(this.chartData, this.chartOptions);
  },
};
</script>

<style scoped>

</style>
