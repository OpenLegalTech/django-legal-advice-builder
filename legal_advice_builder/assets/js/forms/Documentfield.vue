<template>
  <div>
    <div
      @mouseover="toggleHover"
      @mouseleave="toggleHover"
      @click="toggleShowForm"
      v-bind:style="{ cursor: 'pointer' }"
      class="bg-light position-relative"
    >
      <span
        v-if="renderedContent == '' || hover"
        class="
          position-absolute
          badge
          rounded-pill
          bg-white
          text-body
          document-edit-button
        "
      >
        <i class="bi bi-pen-fill"></i> edit
      </span>
      <div
        v-if="renderedContent == '' && !showForm"
        class="position-absolute top-50 start-50 translate-middle"
      >
        {{ this.getEmptyContentPlaceholder() }}
      </div>
      <div
        v-if="!showForm"
        :style="getContentStyles()"
        ref="contentBox"
        v-html="renderedContent"
      ></div>
    </div>
    <div v-if="showForm">
      <editor
        v-model="renderedContentEdited"
        :init="{
          height: this.formheight,
          menubar: false,
          plugins: [
            'advlist autolink lists link image charmap print preview anchor',
            'searchreplace visualblocks code fullscreen',
            'insertdatetime media table paste code help wordcount',
          ],
          toolbar:
            'undo redo | formatselect | bold italic backcolor | \
           alignleft aligncenter alignright alignjustify | \
           bullist numlist outdent indent | removeformat | help',
        }"
      />

      <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-1">
        <button
          class="btn btn-primary btn-sm me-md-2"
          @click="cancel"
          type="button"
        >
          cancel
        </button>
        <button class="btn btn-primary btn-sm" @click="save" type="button">
          save
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import Editor from "@tinymce/tinymce-vue";
export default {
  name: "documentfield",
  components: {
    editor: Editor,
  },
  props: {
    content: String,
    document: String,
    fieldtypeid: String,
    name: String,
  },
  data: function () {
    this.$root.csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    return {
      formheight: 40,
      renderedContent: this.content
        .replaceAll("[[", "{{")
        .replaceAll("]]", "}}"),
      hover: false,
      showForm: false,
      renderedContentEdited: this.content
        .replaceAll("[[", "{{")
        .replaceAll("]]", "}}"),
    };
  },
  mounted() {
    this.formheight = this.matchHeight();
  },
  methods: {
    matchHeight: function () {
      if (this.$refs.contentBox) {
        return this.$refs.contentBox.clientHeight + 100;
      }
    },
    getformStyles: function () {
      return { height: `${this.formheight}px` };
    },
    getContentStyles: function () {
      if (this.renderedContent == "") {
        return { "min-height": `${this.formheight}px` };
      }
      return {};
    },
    getEmptyContentPlaceholder: function () {
      return `< ${this.name} >`;
    },
    toggleHover: function () {
      this.hover = !this.hover;
    },
    toggleShowForm: function () {
      this.showForm = !this.showForm
      this.hover = false
    },
    cancel: function () {
      this.showForm = !this.showForm;
      this.renderedContentEdited = this.renderedContent
    },
    save: function () {
      const data = {
        content: JSON.parse(JSON.stringify(this.renderedContentEdited)),
        document: this.document,
        fieldtypeid: this.fieldtypeid,
      };

      const requestOptions = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.$root.csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify(data),
      };
      fetch(window.location.href, requestOptions)
        .then((response) => response.json())
        .then((data) => {
          this.renderedContent = data.content;
          this.renderedContentEdited = data.content;
          this.showForm = !this.showForm;
        });
    },
  },
};
</script>