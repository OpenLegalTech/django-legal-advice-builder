<template>
  <div class="alert p-3 mb-3 " :class="{'alert-dark': this.newValue=='',
                                        'alert-info': this.newValue=='question',
                                        'alert-success': this.newValue=='success',
                                        'alert-danger': this.newValue=='failure'}">
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

    <div v-if="newValue == 'question'" class="row justify-content-start">
        <div class="col-6">
            <select class="form-select" v-model="jumpToQuestion" @change="onChange">
              <option
                v-for="question, index in questions"
                :key="`${ index }`"
                :value="question.id"
            >{{ question.text }}</option>
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
    questions: Array,
    usedOptions: Array,
    listIndex: Number
  },
  data () {
    const jumpToQuestion = this.condition.then_value.includes('question') ? this.condition.then_value.split('_')[1] : ''
    const newValue = this.condition.then_value.includes('question') ? 'question' : this.condition.then_value
    return {
      newOption: this.condition.if_value,
      newValue: newValue,
      thenOptions: {'success': 'Erfolg: Springe zum nächsten Fragebogen.',
                    'failure': 'Kein Erfolg: Zeige Abbruchnachricht',
                    'question': 'Springe zu Frage:'},
      newCondition: this.condition,
      jumpToQuestion: jumpToQuestion
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
      if(this.newValue == 'question') {
        this.newCondition['then_value'] = `${this.newValue}_${this.jumpToQuestion}`
      } else {
        this.newCondition['then_value'] = this.newValue
      }
      this.$emit('conditionUpdated', this.newCondition, this.listIndex)
    }
  }
};
</script>
