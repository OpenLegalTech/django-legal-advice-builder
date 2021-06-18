<template>
  <div class="row row-cols-lg-2 g-3 align-items-center">
    <div class="col-12">
      <div class="form-group my-3">
        <input type="text" class="form-control" v-model="value" @change="updateChoice"/>
      </div>
    </div>
    <div class="col-12">
      <button class="btn btn-danger" @click="deleteChoice">Delete</button>
    </div>
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
    updateChoice (event) {
      let newValue = {};
      newValue[this.optionKey] = event.target.value;
      this.$emit('choiceUpdated', newValue);
    },
    deleteChoice (event) {
      event.preventDefault();
      this.$emit('choiceDeleted', this.optionKey)
    }
  }
};
</script>
