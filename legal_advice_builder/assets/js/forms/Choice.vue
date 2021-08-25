<template>
  <div class="row align-items-center">
    <div class="col-10">
      <div class="form-group my-3">
        <input type="text" class="form-control" v-model="value" @change="updateChoice"/>
      </div>
    </div>
    <div class="col-2">
      <button class="btn btn-sm btn-outline-danger" @click="deleteChoice">Löschen</button>
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
