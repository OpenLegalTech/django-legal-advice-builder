<template>
  <div>
    <div class="mb-3">
      <input
        type="text"
        v-model="searchString"
        class="form-control"
      />
    </div>
    <table class="table">
      <tbody>
        <template v-for="(value, name, index) in placeholders">
          <tr :key="`${index}`" v-if="value.indexOf(searchString) > -1">
            <td>
              {{ value }}
            </td>
            <td><button class="btn btn-light" @click="copyToClipboard(fullVariable(name))"><i class="bi bi-clipboard" ></i></button></td>
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
    variables: Object,
  },
  data: function () {
    return {
      placeholders: this.variables,
      searchString: ''
    }
  },
  methods: {
    fullVariable(variable) {
      return `{{ answers.${variable} }}`
    },
    copyToClipboard(name) {
      navigator.clipboard.writeText(name)
    }
  }
}
</script>