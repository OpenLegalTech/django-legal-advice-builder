import Vue from 'vue';
import ChoiceField from "./ChoiceField"
import {renderComponent} from '../helpers/vue-helper'


function createChoiceField (selector) {
  new Vue({
    components: { ChoiceField },
    render: renderComponent(selector, ChoiceField)
  }).$mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createChoiceField('#options')
})

export default {
  createChoiceField
}