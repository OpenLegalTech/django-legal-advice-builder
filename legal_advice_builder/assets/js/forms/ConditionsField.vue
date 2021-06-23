<template>
  <div>
    <div v-if="{ success }">
      <Condition
        v-for="(option, index) in success"
        :key="`success_${index}`"
        :selectedOption="`${option}`"
        :value="`${successString}`"
        :options="{ options }"
        :textIf="`${textIf}`"
        :textThen="`${textThen}`"
        @conditionUpdated="conditionUpdated"
      ></Condition>
    </div>
    <div v-if="{ failure }">
      <Condition
        v-for="(option, index) in failure"
        :key="`failure_${index}`"
        :selectedOption="`${option}`"
        :value="`${failureString}`"
        :options="{ options }"
        :textIf="`${textIf}`"
        :textThen="`${textThen}`"
        @conditionUpdated="conditionUpdated"
      ></Condition>
    </div>
  </div>
</template>

<script>
import Condition from "./Condition.vue"
export default {
  components: { Condition },
  name: "conditions-field",
  props: {
    initial: Object,
    options: Object,
    text: Object,
    name: String
  },
  data() {
    let data = {
        failureString: "failure",
        successString: "success",
        textIf: this.text.if,
        textThen: this.text.then,
        formData: this.initial
    };
    return data;
    },
  computed: {
    success () {
      if (this.formData.success[0] !== undefined) {
        return this.formData.success[0].options
      }
      return []
    },
    failure () {
      if (this.formData.failure[0] !== undefined) {
        return this.formData.failure[0].options
      }
      return []
    }
  },
  methods: {
    updateFormField: function () {
      document.getElementsByName(this.name)[0].value = JSON.stringify(this.formData)
    },
    conditionUpdated: function (newValue) {
      const status = newValue.status
      const option = newValue.option
      let newSuccessOptions = JSON.parse(JSON.stringify(this.success))
      let newFailureOptions = JSON.parse(JSON.stringify(this.failure))
      if (status == 'success') {
        if(!newSuccessOptions.includes(option)) {
          newSuccessOptions.push(option)
        }
        if(newFailureOptions.includes(option)) {
          const index = newFailureOptions.indexOf(option)
          newFailureOptions.splice(index, 1)
        }
      }
      if (status == 'failure') {
        if(!newFailureOptions.includes(option)) {
          newFailureOptions.push(option)
        }
        if(newSuccessOptions.includes(option)) {
          const index = newSuccessOptions.indexOf(option)
          newSuccessOptions.splice(index, 1)
        }
      }
      this.formData = {
        'success': [{'options': newSuccessOptions}],
        'failure': [{'options': newFailureOptions}]
      }
      this.updateFormField()
      this.$forceUpdate()
    }
  },
  mounted () {}
}
</script>