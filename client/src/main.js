import Vue from 'vue'
import Routes from './routes';
import VueRouter from 'vue-router';
import VueAutosuggest from "vue-autosuggest";
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue';

Vue.use(BootstrapVue);
Vue.use(IconsPlugin);
Vue.use(VueAutosuggest);
Vue.use(VueRouter);

Vue.config.productionTip = false

const router = new VueRouter({
  routes: Routes,
  mode: "history",
});

import App from './App.vue'
new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
