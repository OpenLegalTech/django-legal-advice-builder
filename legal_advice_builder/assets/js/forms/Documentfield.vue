<template>
  <div>
    <div
      @mouseover="toggleHover"
      @mouseleave="toggleHover"
      @click="toggleShowForm"
      v-bind:style="{ cursor: 'pointer' }"
      class="bg-light position-relative my-2"
    >
      <div
        v-if="this.newQuestion !== '' && this.newIfValue !== '' && !showForm"
        class="
          opacity-50
          position-absolute
          top-50
          start-50
          translate-middle
          bg-dark
          text-white
          p-1
        "
      >
        <small>Condition</small>
        <p class="mb-0">{{ this.getText() }} - {{ this.newIfValue }}</p>
      </div>
      <div
        v-if="!showForm"
        :style="getContentStyles()"
        ref="contentBox"
        v-html="renderedContent"
      ></div>
    </div>

    <div v-if="showForm" class="card">
      <div class="card-header text-end p-1 border-0">
        <span
          @click="toggleShowForm"
          :style="{ cursor: 'pointer' }"
          class="badge rounded-pill bg-transparent text-body"
        >
          <i class="bi bi-x-lg"></i>
        </span>
      </div>
      <div class="card-body bg-light">
        <div
          v-if="showForm && !showConditionForm && !newQuestion && !newIfValue"
          class="opacity-50 bg-dark text-white p-2"
        >
          <small>Condition</small>
          <p class="mb-0">This textblock is always displayed</p>
          <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-2">
            <button @click="toggleConditionShowForm" class="btn btn-dark border btn-sm" type="button">
              <i class="bi bi-pencil-fill"></i>
            </button>
          </div>
        </div>

        <div
          v-if="showForm && !showConditionForm && newQuestion && newIfValue"
          class="opacity-50 bg-dark text-white p-2"
        >
          <small>Condition</small>
          <p class="mb-0">{{ this.getText() }} - {{ this.newIfValue }}</p>
          <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-2">
            <button @click="resetCondition" class="btn btn-dark border btn-sm me-md-1" type="button"><i class="bi bi-trash"></i></button>
            <button @click="toggleConditionShowForm" class="btn btn-dark border btn-sm" type="button">
              <i class="bi bi-pencil-fill"></i>
            </button>
          </div>
        </div>

        <small v-if="showForm && showConditionForm"
          >Show this textblock only when the answer to the question
        </small>
        <div v-if="showForm && showConditionForm">
          <div class="row g-3 mb-3">
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
          </div>
        </div>
      </div>
      <div class="card-body bg-light">
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
        <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-3">
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
      this.showForm = !this.showForm;
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
          this.showForm = !this.showForm;
          this.textblockid = data.id;
        });
    },
  },
};
</script>