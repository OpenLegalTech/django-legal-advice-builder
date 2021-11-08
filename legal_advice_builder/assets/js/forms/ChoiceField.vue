<template>
  <div class="border p-3" :class="{'border-danger border': this.count==0}">
    <Choice v-for="(value, name, index) in choices"
      :key="`${ name }-${ index }`"
      :choiceKey="`${ name }`"
      :choiceValue="`${ value }`"
      @choiceUpdated="choiceUpdated"
      @choiceDeleted="choiceDeleted"
    >
    </Choice>
    <div class="row align-items-center">
      <div class="col-10">
        <div class="form-group my-3">
          <input type="text" class="form-control" v-model="newChoice"/>
        </div>
      </div>
      <div class="col-2">
        <button class="btn btn-primary btn-sm" @click.prevent="addChoice">Hinzufügen</button>
      </div>
    </div>
  </div>
</template>

<script>
import Choice from './Choice.vue'
export default {
  components: { Choice },
  name: 'choice-field',
  props: {
    initial: Object,
    inputtype: String,
    name: String,
    thenOptions: Object
  },
  data: function () {
    return {
      choices: this.initial,
      newChoice: ''
    };
  },
  methods: {
    updateFormField: function () {
      document.getElementsByName(this.name)[0].value = JSON.stringify(this.choices)
    },
    choiceUpdated: function (choice) {
      let choiceKey = Object.keys(choice)[0]
      let choiceValue = choice[choiceKey]
      this.choices[choiceKey] = choiceValue
      this.updateFormField()
    },
    choiceDeleted: function (choiceKey) {
      delete this.choices[choiceKey]
      this.updateFormField()
      this.$forceUpdate()
    },
    addChoice: function () {
      let choiceCount = Object.keys(this.choices).length + 1
      let newKey = `${ this.name }_${ choiceCount }`
      this.choices[newKey] = this.newChoice
      this.newChoice = ''
      this.updateFormField()
      this.$forceUpdate()
    }
  },
}
</script>
