import { createRouter, createWebHashHistory } from 'vue-router';
import Home from './views/Home.vue';
import Records from './views/Records.vue';
import Forecast from './views/Forecast.vue';

const routes = [
  {
    name: 'home',
    path: '/',
    component: Home,
  },
  {
    name: 'records',
    path: '/records',
    component: Records,
  },
  {
    name: 'forecast',
    path: '/forecast/:patientId',
    component: Forecast,
    props: true,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
