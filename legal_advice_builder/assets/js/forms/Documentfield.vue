<template>
  <div>
    <div
      @mouseenter="toggleHover"
      @mouseleave="toggleHover"
      v-bind:style="{ cursor: 'pointer' }"
      class="position-relative my-2 px-3 pt-3 pb-1"
      :class="{
        'bg-light': hover && !showForm && !showConditionForm,
        'bg-primary': showForm || showConditionForm,
      }"
    >
      <div
        v-if="!showForm && !showConditionForm && hover"
        class="
          position-absolute
          btn-group
          border
          top-0
          start-50
          translate-middle
        "
        role="group"
        aria-label="Basic example"
      >
        <button
          title="edit text"
          type="button"
          @click="toggleShowForm"
          class="btn bg-white text-body btn-sm"
        >
          <i class="bi bi-pencil"></i>
        </button>
        <button
          title="edit condition"
          type="button"
          @click="toggleConditionShowForm"
          class="btn bg-white text-body btn-sm"
        >
          <i class="bi bi-option"></i>
        </button>
        <button
          title="delete textblock"
          type="button"
          class="btn bg-white text-body btn-sm"
        >
          <i class="bi bi-trash"></i>
        </button>
      </div>

      <div
        v-if="!showForm && !showConditionForm"
        :style="getContentStyles()"
        ref="contentBox"
        v-html="renderedContent"
      ></div>

      <div v-if="showForm">
        <editor
          v-model="renderedContentEdited"
          :init="{
            height: this.formheight,
            menubar: false,
            entity_encoding: 'raw',
            plugins: [
              'advlist autolink lists link image charmap print preview anchor',
              'searchreplace visualblocks code fullscreen',
              'insertdatetime media table paste code help wordcount',
            ],
            toolbar:
              'undo redo | formatselect | bold italic | \
           alignleft aligncenter alignright alignjustify | \
           bullist numlist outdent indent | removeformat | help',
          }"
        />
        <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-3 mb-1">
          <button
            class="btn btn-outline-light btn-sm me-md-2"
            @click="cancel"
            type="button"
          >
            cancel
          </button>
          <button class="btn btn-success btn-sm" @click="save" type="button">
            save
          </button>
        </div>
      </div>

      <div v-if="showConditionForm">
        <div class="bg-white" :style="getformStyles()">
          <div
            class="alert alert-primary d-flex align-items-center rounded-0"
            role="alert"
          >
            <p v-if="!newIfValue">This Textblock is always displayed.</p>
            <p v-if="newQuestion && newIfValue">This Textblock only displayed when the answer to "{{ this.getText() }}" is  "{{ this.newIfValue }}".</p>
          </div>
          <div>
            <div class="row g-3 mb-3 mx-1">
              <div class="col-sm-7">
                <select
                  class="form-select"
                  v-model="newQuestion"
                  @change="options = getOptions()"
                >
                  <option
                    v-for="(question, index) in questions"
                    :value="question.id"
                    :key="`${index}`"
                  >
                    {{ question.text }}
                  </option>
                </select>
              </div>
              <div class="col-sm-3" v-if="newQuestion !== ''">
                <select class="form-select" v-model="newIfValue">
                  <option
                    v-for="(optionValue, optionKey, index) in options"
                    :value="optionValue"
                    :key="`${index}`"
                  >
                    {{ optionValue }}
                  </option>
                </select>
              </div>
              <div class="col-sm-3" v-if="newQuestion !== ''">
                <button
                  @click="resetCondition"
                  class="btn btn-outline-light btn-sm me-md-1"
                  type="button"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-3 mb-1">
          <button
            class="btn btn-outline-light btn-sm me-md-2"
            @click="cancel"
            type="button"
          >
            cancel
          </button>
          <button class="btn btn-success btn-sm" @click="save" type="button">
            save
          </button>
        </div>
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
    document: Number,
    textblock: Number,
    name: String,
    if_option: String,
    if_value: String,
    question: String,
    questions: Array,
  },
  data: function () {
    this.$root.csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    return {
      formheight: 40,
      renderedContent: this.content,
      hover: false,
      showForm: false,
      showConditionForm: false,
      textblockid: this.textblock,
      renderedContentEdited: this.content,
      newQuestion: this.question,
      newIfValue: this.if_value,
      options: {},
    };
  },
  mounted() {
    this.formheight = this.matchHeight();
    this.options = this.getOptions();
  },
  methods: {
    matchHeight: function () {
      if (this.$refs.contentBox) {
        return this.$refs.contentBox.clientHeight + 100;
      }
    },
    getOptions: function () {
      if (this.newQuestion !== "" && this.questions.length > 0) {
        for (let i = 0; i < this.questions.length; i++) {
          if (this.questions[i].id.toString() == this.newQuestion) {
            return this.questions[i].options;
          }
        }
      }
      return {};
    },
    getText: function () {
      if (this.newQuestion !== "" && this.questions.length > 0) {
        for (let i = 0; i < this.questions.length; i++) {
          if (this.questions[i].id.toString() == this.newQuestion) {
            return this.questions[i].text;
          }
        }
      }
      return {};
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
    resetCondition: function () {
      this.newQuestion = "";
      this.newIfValue = "";
    },
    toggleHover: function () {
      this.hover = !this.hover;
    },
    toggleShowForm: function () {
      this.showForm = !this.showForm;
      this.hover = false;
    },
    toggleConditionShowForm: function () {
      this.showConditionForm = !this.showConditionForm;
    },
    cancel: function () {
      this.showForm = false;
      this.showConditionForm = false;
      this.hover = false;
      this.newQuestion = this.question;
      this.newIfValue = this.if_value;
      this.renderedContentEdited = this.renderedContent;
    },
    save: function () {
      const data = {
        content: JSON.parse(JSON.stringify(this.renderedContentEdited)),
        document: this.document,
        textblock: this.textblockid,
        question: this.newQuestion,
        if_value: this.newIfValue,
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
          this.showForm = false;
          this.showConditionForm = false;
          this.hover = false;
          this.textblockid = data.id;
        });
    },
  },
};
</script>