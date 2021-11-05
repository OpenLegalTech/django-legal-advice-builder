import Vue from 'vue';
import Placeholder from "./Placeholder"

Vue.component("placeholder", Placeholder)

new Vue({
  el: "#placeholders",
  render: (createElement) => {
    return createElement(Placeholder)
  },
})