<template>
    <div class="container col-12">
      <translation-input ref="transInput" class="mb-4"
          v-on:jump-clicked="onJumpClicked"
          v-on:translate-clicked="onTranslateClicked" />
      <div class="container col-xm-12 col-sm-12 col-lg-7"
          id="app">
        <translation-list ref="entries"
            v-on:new-translation="onNewTranslation"/>
      </div>
        
    </div>
</template>

<script>
import TranslationInput from '@/components/TranslationInput'
import TranslationList from '@/components/TranslationList'

export default {
    name: 'app',
    components: {TranslationInput, TranslationList},
    methods: {
        onTranslateClicked: function (event) {
            this.$refs.entries.addScript(event)
        },

        onJumpClicked: function (event) {
            this.$refs.entries.onJumpClick()
        },

        onNewTranslation: function (event) {
            this.$refs.transInput.onNewTranslation()
        }
    }

}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /*text-align: center;*/
  color: #2c3e50;
  margin-top: 60px;
}

#scriptlist {
    overflow-y: auto;
    margin: 12em 0em 0em 0em;
}

#top-panel {
    height: 10em;
    width: 100%;
    z-index: 100;
    background-color: white;
    border-bottom: 2px solid lightgray;
}

#trans-input {
    margin-top: 1em;
    margin-bottom: 1em;
}

#indicator {
    z-index: 1000;
    position: fixed;
    left: 100px;
    top: 300px;
    width: 10em;
}

.justTranslated {
    background-color: lightblue;
}

.script {
    margin: 1em 0em 1em 0em;
    padding: 0.7em 0.3em 0.7em 0.3em;
}

#scriptlist {
    padding: 0em;
}

#buttons {
    margin-left: 0.7em;
    margin-right: 0em;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.initial, .translated {
    border: 1px solid lightgray;
    border-radius: 0.4em;
    padding: 0.4em;
}

.new-translation {
    background-color: red;
}
</style>
