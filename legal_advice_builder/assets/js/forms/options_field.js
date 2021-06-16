// import Vue from "vue";
// import OptionsField from "./OptionsField.vue";

// new Vue({
//   render: (h) => h(OptionsField),
// }).$mount("#options");


//import Vue from "vue";

// import components
import Vue from 'vue/dist/vue.js';

Vue.component(
  "options-field",
  require("./OptionsField.vue").default
);

let vue = new Vue({
  //
}).$mount("#options");
