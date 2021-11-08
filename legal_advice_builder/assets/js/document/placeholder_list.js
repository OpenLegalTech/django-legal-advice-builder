import Vue from 'vue';
import Placeholder from "./Placeholder"
import {renderComponent} from '../helpers/vue-helper'


function createPlaceholderList (selector) {
  new Vue({
    components: { Placeholder },
    render: renderComponent(selector, Placeholder)
  }).$mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createPlaceholderList('#placeholders')
})

export default {
  createPlaceholderList
}