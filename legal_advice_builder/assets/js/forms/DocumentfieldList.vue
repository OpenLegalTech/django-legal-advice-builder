<template>
  <div>
    <DocumentField
      v-for="(field, index) in fieldlist"
      :key="`${name}-${index}`"
      :content="field.content"
      :document="field.document"
      :name="field.name"
      :textblock="field.textblock"
    ></DocumentField>
    <div class="d-grid gap-2 mt-5">
      <button class="btn btn-primary btn-sm" @click="addField" type="button">
        Button
      </button>
    </div>
  </div>
</template>

<script>
import DocumentField from "./Documentfield.vue";
export default {
  name: "documentfieldlist",
  props: {
    document: String,
    fieldtypeid: String,
    initial: Array
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
        textblock: '',
        name: this.name,
      })
    },
  },
};
</script>
