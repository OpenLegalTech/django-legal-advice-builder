import Vue from 'vue';

Vue.component(
  "conditions-field",
  require("./ConditionsField.vue").default
);

let vue = new Vue({}).$mount("#conditions");
