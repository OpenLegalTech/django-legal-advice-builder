<template>
  <div :class="{'alert p-3 mb-3 alert-success': this.condition.then_value=='success', 'alert p-3 mb-3 alert-danger': this.condition.then_value=='failure'}">
    <div class="row justify-content-start">
      <div class="col-4">
          {{ textIf }}
      </div>
    </div>

    <div class="row justify-content-start">
      <div class="col-6">
          <select class="form-select" v-model="newOption" @change="onChange">
              <option
                v-for="optionValue, optionKey, index in availableOptions"
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
    condition: Object,
    textIf: String,
    textThen: String,
    options: Object,
    usedOptions: Array,
    listIndex: Number
  },
  data () {
    return {
      newOption: this.condition.if_value,
      newValue: this.condition.then_value,
      thenOptions: {'success': 'Erfolg: Springe zum nächsten Fragebogen.',
                    'failure': 'Kein Erfolg: Zeige Abbruchnachricht'},
      newCondition: this.condition
    }
  },
  computed: {
    availableOptions () {
      let options = JSON.parse(JSON.stringify(this.options))
      this.usedOptions.forEach(option => {
        if(option !== this.condition.if_value) {
          delete options[option]
        }
      })
      return options
    }
  },
  methods: {
    onChange () {
      this.newCondition['if_value'] = this.newOption
      this.newCondition['then_value'] = this.newValue
      this.$emit('conditionUpdated', this.newCondition, this.listIndex)
    }
  }
};
</script>
