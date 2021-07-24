import Vue from 'vue/dist/vue.js';

Vue.component(
  "document-field",
  require("./Documentfield.vue").default
);

let vue = new Vue({}).$mount("#app");
