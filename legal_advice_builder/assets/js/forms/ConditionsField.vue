<template>
    <div>
        <div v-if="{success}">
            <Condition v-for="option, index in success"
                :key="`success_${ index }`"
                :selectedOption="`${ option }`"
                :value="`${ successString }`"
                :options={options}
                :textIf="`${ textIf }`"
                :textThen="`${ textThen }`"
            ></Condition>
        </div>
        <div v-if="{failure}">
            <Condition v-for="option, index in failure"
                :key="`failure_${ index }`"
                :selectedOption="`${ option }`"
                :value="`${ failureString }`"
                :options={options}
                :textIf="`${ textIf }`"
                :textThen="`${ textThen }`"
            ></Condition>
        </div>
    </div>
</template>

<script>
import Condition from './Condition.vue'
export default {
  components: { Condition },
  name: 'conditions-field',
  props: {
    initial: Object,
    options: Object,
    text: Object
  },
  data () {
      let data = {
          failureString: 'failure',
          successString: 'success',
          success: undefined,
          failure: undefined,
          textIf: this.text.if,
          textThen: this.text.then
      }
      if(this.initial.success[0] !== undefined) {
          data.success = this.initial.success[0].options
      }
      if(this.initial.failure[0] !== undefined) {
          data.failure = this.initial.failure[0].options
      }
      return data
  }

}
</script>