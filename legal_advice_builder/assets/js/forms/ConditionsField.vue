<template>
  <div>
      <Condition
        v-for="condition, index in formData"
        :key="index"
        :listIndex="index"
        :condition="condition"
        :options="options"
        :textIf="`${textIf}`"
        :textThen="`${textThen}`"
        :usedOptions="usedOptions"
        :questions="questions"
        :thenoptions="thenoptions"
        @conditionUpdated="conditionUpdated"
      ></Condition>
  </div>
</template>

<script>
import Condition from "./Condition.vue"
export default {
  components: { Condition },
  name: "conditions-field",
  props: {
    initial: Array,
    options: Object,
    text: Object,
    name: String,
    questions: Array,
    question: String,
    thenoptions: Object
  },
  data() {
    let data = {
        textIf: this.text.if,
        textThen: this.text.then,
        formData: this.initial
    };
    return data;
  },
  computed: {
    usedOptions() {
      let usedOptions = []
      this.formData.map(function(condition, index) {
        usedOptions.push(condition.if_value)
      })
      return usedOptions
    }
  },
  mounted() {
    for (const [key, value] of Object.entries(this.options)) {
      if(!this.usedOptions.includes(key)) {
        const emptyCondition = {
          if_option: 'is',
          question: this.questions,
          if_value: key,
          then_value: ''
        }
        this.formData.push(emptyCondition)
      }
    }
  },
  methods: {
    updateFormField: function () {
      document.getElementsByName(this.name)[0].value = JSON.stringify(this.formData)
    },
    conditionUpdated: function (newValue, listIndex) {
      this.formData.splice(listIndex, 1, newValue)
      this.updateFormField()
      this.$forceUpdate()
    }
  }
}
</script>