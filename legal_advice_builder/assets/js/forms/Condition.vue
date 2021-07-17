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

    <div v-if="questiontype == 'DT'" class="row justify-content-start">
      <div class="col-3">
          <input type="number" min="1" max="365" @change="onChange" class="textinput textInput form-control" v-model="period">
      </div>
      <div class="col-3">
          <select class="form-select" v-model="unit" @change="onChange">
              <option
                v-for="optionValue, optionKey, index in periodoptions"
                :value="optionKey"
                :key="`${ index }`"
              >{{optionValue}}</option>
          </select>
      </div>
    </div>

    <div v-if="Object.keys(ifoptions).length > 1" class="row justify-content-start">
      <div class="col-6">
          <select class="form-select" v-model="newIfOption" @change="onChange">
              <option
                v-for="optionValue, optionKey, index in ifoptions"
                :value="optionKey"
                :key="`${ index }`"
              >{{optionValue}}</option>
          </select>
      </div>
    </div>

    <div v-if="questiontype !== 'DT'" class="row justify-content-start">
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
                v-for="optionValue, optionKey, index in thenoptions"
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
    defaultnext: String,
    textIf: String,
    textThen: String,
    options: Object,
    questions: Array,
    usedOptions: Array,
    listIndex: Number,
    thenoptions: Object,
    ifoptions: Object,
    periodoptions: Object,
    questiontype: String
  },
  data () {
    let unit = ''
    let period = ''
    const jumpToQuestion = this.condition.then_question ? this.condition.then_question : this.defaultnext
    const newValue = this.condition.then_value ? this.condition.then_value : 'question'

    if (this.questiontype == 'DT' && this.condition.if_value !== '') {
      unit = this.condition.if_value.split('_')[0]
      period = this.condition.if_value.split('_')[1].slice(-1)
    }

    return {
      newIfOption: this.condition.if_option,
      newOption: this.condition.if_value,
      newValue: newValue,
      newCondition: this.condition,
      jumpToQuestion: jumpToQuestion,
      unit: unit,
      period: period
    }
  },
  computed: {
    availableOptions () {
      let options = JSON.parse(JSON.stringify(this.options))
      if (this.questiontype == 'SO' || this.questiontype == 'MO') {
        this.usedOptions.forEach(option => {
          if(option !== this.condition.if_value) {
            delete options[option]
          }
        })
      }
      return options
    }
  },
  methods: {
    onChange () {
      this.newCondition['if_option'] = this.newIfOption
      this.newCondition['if_value'] = this.newOption
      if (this.questiontype == 'DT') {
        this.newCondition['if_value'] = `${this.unit}_+${this.period}`
      }
      if(this.newValue == 'question') {
        this.newCondition['then_value'] = `${this.newValue}`
        this.newCondition['then_question'] = `${this.jumpToQuestion}`
      } else {
        this.newCondition['then_value'] = this.newValue
      }
      this.$emit('conditionUpdated', this.newCondition, this.listIndex)
    }
  }
};
</script>
