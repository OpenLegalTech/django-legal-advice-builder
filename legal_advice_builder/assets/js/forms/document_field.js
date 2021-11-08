import Vue from 'vue';
import DocumentfieldList from "./DocumentfieldList"
import {renderComponent} from '../helpers/vue-helper'


function createDocumentfieldList (selector) {
  new Vue({
    components: { DocumentfieldList},
    render: renderComponent(selector, DocumentfieldList)
  }).$mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createDocumentfieldList('#app')
})

export default {
  createDocumentfieldList
}
