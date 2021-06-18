<template>
  <div>
    <div>
      <Choice v-for="(value, name, index) in initial"
        :key="`${ name }-${ index }`"
        :optionKey="`${ name }`"
        :optionValue="`${ value }`"
        @choiceUpdated="choiceUpdated"
      >
      </Choice>
    </div>
  </div>
</template>

<script>
import Choice from './Choice.vue'
export default {
  components: { Choice },
  name: 'options-field',
  props: {
    initial: Object,
    inputtype: String,
    name: String
  },
  methods: {
    choiceUpdated: function (event, key, value) {
      debugger
    },
  },
}
</script>
