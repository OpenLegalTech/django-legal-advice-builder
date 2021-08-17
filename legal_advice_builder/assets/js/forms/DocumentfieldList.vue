<template>
  <div>
    <DocumentField
      v-for="(field, index) in fieldlist"
      :listindex="index"
      :key="`${field.textblock}-${index}`"
      :content="field.content"
      :document="field.document"
      :name="field.name"
      :textblock="field.textblock"
      :question="field.question.toString()"
      :if_option="field.if_option"
      :if_value="field.if_value"
      :questions="questions"
      @deleteField="deleteField"
    ></DocumentField>
    <div class="d-grid gap-2 mt-5 mx-3 mb-3">
      <button class="btn btn-primary" @click="addField" type="button">
        <i class="bi bi-plus"></i> Add text block
      </button>
    </div>
  </div>
</template>

<script>
import DocumentField from "./Documentfield.vue";
export default {
  name: "documentfieldlist",
  props: {
    document: Number,
    initial: Array,
    questions: Array
  },
  components: {
    DocumentField,
  },
  data: function () {
    return {
      fieldlist: this.initial,
      name: 'name'
    }
  },
  methods: {
    addField: function () {
      this.initial.push({
        content: "",
        document: this.document,
        name: this.name,
        textblock: '',
        question: '',
        if_option: '',
        if_value: '',
      })
    },
    deleteField: function (index, textblock) {
      this.$delete(this.fieldlist, index);
    }
  },
};
</script>
