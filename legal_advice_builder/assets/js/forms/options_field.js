import Vue from 'vue/dist/vue.js';

Vue.component(
  "options-field",
  require("./OptionsField.vue").default
);

let vue = new Vue({}).$mount("#options");
