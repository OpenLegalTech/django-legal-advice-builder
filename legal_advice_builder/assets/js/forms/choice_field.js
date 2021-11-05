import Vue from 'vue';

Vue.component(
  "choice-field",
  require("./ChoiceField.vue").default
);

let vue = new Vue({}).$mount("#options");
