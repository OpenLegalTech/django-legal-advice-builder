<template>
  <div :class="{'alert p-3 mb-3 alert-success': this.value=='success', 'alert p-3 mb-3 alert-danger': this.value=='failure'}">
    <div class="row justify-content-start">
      <div class="col-4">
          {{ textIf }}
      </div>
    </div>

    <div class="row justify-content-start">
      <div class="col-6">
          <select class="form-select" v-model="newOption" @change="onChange">
              <option
                v-for="optionValue, optionKey, index in options.options"
                :value="optionKey"
                :key="`${ index }`"
              >{{optionValue}}</option>
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
            <select class="form-select" v-model="newValue" @change="onChange">
              <option
                v-for="optionValue, optionKey, index in thenOptions"
                :key="`${ index }`"
                :value="optionKey"
            >{{optionValue}}</option>
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
      newOption: this.selectedOption,
      newValue: this.value,
      thenOptions: {'success': 'Erfolg: Springe zum nächsten Fragebogen.',
                    'failure': 'Kein Erfolg: Zeige Abbruchnachricht'}
    }
  },
  methods: {
    onChange () {
      let newValue = {
        'status': this.newValue,
        'option': this.newOption
      }
      this.$emit('conditionUpdated', newValue)
    }
  }
};
</script>
