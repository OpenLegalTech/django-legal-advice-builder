import Vue from 'vue/dist/vue.js';

Vue.component(
  "conditions-field",
  require("./ConditionsField.vue").default
);

let vue = new Vue({}).$mount("#conditions");
