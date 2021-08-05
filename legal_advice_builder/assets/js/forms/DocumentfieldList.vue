<template>
  <div>
    <DocumentField
      v-for="(field, index) in initial"
      :key="`${name}-${index}`"
      :content="field.content"
      :document="field.document"
      :name="field.name"
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
  components: {
    DocumentField,
  },
  data: function () {
    return {
      initial: [
        {
          content: "hallo",
          document: "document",
          fieldtypeid: "3",
          name: "name",
        },
      ],
    };
  },
  methods: {
    addField: function () {
      this.initial.push({
        content: "hallo",
        document: "document",
        fieldtypeid: "3",
        name: "name",
      });
    },
  },
};
</script>
