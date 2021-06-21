<template>
  <div :class="{'alert p-3 mb-3 alert-success': this.value=='success', 'alert p-3 mb-3 alert-danger': this.value=='failure'}">
    <div class="row justify-content-start">
      <div class="col-4">
          {{ textIf }}
      </div>
    </div>

    <div class="row justify-content-start">
      <div class="col-6">
          <select class="form-select">
              <option v-for="option, key, index in options.options" :key="`${ index }`" :selected="selectedOption === key">{{option}}</option>
          </select>
      </div>
    </div>

    <div class="row justify-content-start">
      <div class="col-4">
          {{ textThen }}
      </div>
    </div>

    <div class="row justify-content-start">
        <div class="col-6">
            <select class="form-select">
              <option v-for="option, index in thenOptions" :key="`${ index }`" :selected="option === value">{{option}}</option>
          </select>
        </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "condition",
  props: {
    selectedOption: String,
    value: String,
    textIf: String,
    textThen: String,
    options: Object,
  },
  data () {
    return {
      thenOptions: ['success', 'failure']
    }
  }
};
</script>
