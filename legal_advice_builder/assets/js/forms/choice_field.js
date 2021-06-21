import Vue from 'vue/dist/vue.js';

Vue.component(
  "choice-field",
  require("./ChoiceField.vue").default
);

let vue = new Vue({}).$mount("#options");
