<template>
  <div>
    <div class="mb-3">
      <input
        type="text"
        v-model="searchString"
        placeholder="Nach Platzhalter suchen ..."
        class="form-control"
      />
    </div>
    <table class="table">
      <tbody>
        <template v-for="(value, name, index) in searchlist">
          <tr
            :key="`${index}`"
            v-if="
              value.indexOf(searchString) > -1 ||
              name.indexOf(searchString) > -1
            "
          >
            <td>
              {{ value }}<br />
              <small>{{ fullVariable(name) }}</small>
            </td>
            <td>
              <button
                class="btn btn-light"
                @click="copyToClipboard(fullVariable(name))"
              >
                <i class="bi bi-clipboard"></i>
              </button>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: "placeholders",
  props: {
    placeholders: Object,
  },
  data: function () {
    return {
      searchlist: this.placeholders,
      searchString: "",
    };
  },
  methods: {
    fullVariable(variable) {
      return `{{ answers.${variable} }}`;
    },
    copyToClipboard(name) {
      navigator.clipboard.writeText(name);
    },
  },
};
</script>