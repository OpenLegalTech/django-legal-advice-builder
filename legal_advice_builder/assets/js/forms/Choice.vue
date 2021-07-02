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
  name: "choice",
  props: {
    choiceKey: String,
    choiceValue: String,
  },
  data: function () {
    return {
      value: this.choiceValue,
    };
  },
  methods: {
    updateChoice (event) {
      let newValue = {};
      newValue[this.choiceKey] = event.target.value;
      this.$emit('choiceUpdated', newValue);
    },
    deleteChoice (event) {
      event.preventDefault();
      this.$emit('choiceDeleted', this.choiceKey)
    }
  }
};
</script>
