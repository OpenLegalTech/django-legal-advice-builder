import Vue from 'vue';

Vue.component(
  "document-field",
  require("./Documentfield.vue").default
);

Vue.component(
  "document-field-list",
  require("./DocumentfieldList.vue").default
);

let vue = new Vue({}).$mount("#app");
