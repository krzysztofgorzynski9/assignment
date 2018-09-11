<template>
<div id="top-panel" class="container fixed-top col-12">
    <div id="trans-input" class="container input-group col-xs-12 col-sm-12 col-lg-7">
      <textarea rows="5" placeholder="Type English text" v-model="script" class="form-control" aria-label="With textarea"></textarea>
      <div id="buttons" class="row">
          <button id="translate-btn" v-on:click="onTranslateClick" class="btn btn-primary">Translate</button>
          <button id="jumpt-btn"
              v-on:click="onJumpClick"
              v-bind:class="{ 'new-translation':unseenTranslation }"
              class="btn btn-primary">Show new</button>
      </div>
    </div>
    
</div>
</template>

<script charset="utf-8">
export default {
    name: 'translation-input',
    data () {
        return {
            script: '',
            unseenTranslation: false
        }
    },
    methods: {
        onTranslateClick: function (event) {
            this.$emit('translate-clicked', this.script)
        },

        onNewTranslation: function () {
            console.log('New translation')
            this.$set(this, 'unseenTranslation', true)
        },

        onJumpClick: function (event) {
            this.$set(this, 'unseenTranslation', false)
            this.$emit('jump-clicked')
        }
    }
}
</script>
