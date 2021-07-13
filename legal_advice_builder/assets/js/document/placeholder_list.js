import Vue from 'vue/dist/vue.js';

Vue.component(
  "placeholders",
  require("./Placeholder.vue").default
);

new Vue({}).$mount("#placeholders");
