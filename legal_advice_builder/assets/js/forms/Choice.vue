<template>
  <div class="form-group">
    <input type="text" class="form-control" v-model="value" @change="updateChoice"/>
  </div>
</template>

<script>
export default {
  name: "fieldOption",
  props: {
    optionKey: String,
    optionValue: String,
  },
  data: function () {
    return {
      value: this.optionValue,
    };
  },
  methods: {
    updateChoice: function (event) {
      debugger
      this.$emit("choiceUpdated", this.optionValue, this.value);
    },
  },
};
</script>
