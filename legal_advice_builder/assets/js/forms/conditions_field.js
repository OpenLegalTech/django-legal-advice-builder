import Vue from 'vue'
import ConditionsField from "./ConditionsField"
import {renderComponent} from '../helpers/vue-helper'


function createConditionsField (selector) {
  new Vue({
    components: { ConditionsField },
    render: renderComponent(selector, ConditionsField)
  }).$mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createConditionsField('#conditions')
})

export default {
  createConditionsField
}
