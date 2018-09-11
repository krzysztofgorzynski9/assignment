<template>
    <div id="scriptlist" class="container">
        <div :id="script.id" class="script" v-for="script in translatedScripts.concat(pendingScripts)">
            <p class="initial">
                {{ script.content }}
            </p>
            <p class="translated"
               v-if="script.status === 'translated'"
               v-bind:class="{ 'justTranslated':script.id === jumpTo }">
                {{ script.translated }}
            </p>
        </div>
    </div>
</template>


<script>

/* eslint-disable */
import axios from 'axios'

const OnLineConnector = {
    getScript: async function (scriptId) {
        return await axios.get(appUrl + '/scripts', {
            params: {id: scriptId}
        })
    },

    getScripts: async function() {
        return await axios.get(appUrl + '/scripts')
    },

    sendScriptBackend: async function (newId, script) {
        var resp = await axios.post(appUrl + '/script', {
            newId: newId,
            content: script
        })
        return resp.data.id
    },

    getTranslated: async function(pendingIds) {
        return await axios.get(appUrl + '/scripts', {
            params: {ids: JSON.stringify(pendingIds)}
        })
    },
}

var offLineScripts = {}

const OffLineConnector = {
    getScript: async function(scriptId) {
        var scr =  offLineScripts[scriptId]
        const merged = {
            status: 'translated',
            'translated': scr.content + " -- Translated",
            ...scr}
        return merged
    },

    sendScriptBackend: async function(newId, script) {
        offLineScripts[newId] = {
            id: newId,
            status: 'pending',
            content: script}
    },

    getScripts: async function() {
        return {data: Object.values(offLineScripts)}
    },

    getTranslated: async function() {
        return Object.keys(offLineScripts)
    }
}


const appUrl = 'http://localhost/trans'

export default {
    name: 'translation-list',
    connectors: {
        offline: OffLineConnector,
        online: OnLineConnector
    },

    data () {
        return {
            scripts: {},
            jumpTo: ''
        }
    },

    computed: {
        pendingScripts: function () {
            return Object.values(this.scripts)
                .filter(s => s.status === 'pending')
        },

        translatedScripts: function () {
            return Object.values(this.scripts).filter(s => {
                return s.status === 'translated'
            }).sort(function(s1, s2) {
                /* Although browsers could handle simply
                 *  return s1c <= s2c
                 * PhantomJS which runs unit tests cannot
                 * correctly interpret the result of such comparison,
                 * which breaks sorting.
                 */
                const s1c = s1.translated.length
                const s2c = s2.translated.length
                if (s1c < s2c)
                    return -1
                else if (s1c === s2c)
                    return 0
                else
                    return 1
            })
        }
    },

    methods: {

        onJumpClick: function () {
            const target = document.getElementById(this.jumpTo)
            if (target) {
                window.scrollTo(0, target.offsetTop)
            }
        },

        fetchScripts: async function() {
            const resp = await this.connector.getScripts()
            const scripts = resp.data
            for (var i = 0; i < scripts.length; i++) {
                const sc = scripts[i]
                this.$set(this.scripts, sc.id, {
                    id: sc.id.toString(),
                    status: sc.status,
                    content: sc.content,
                    translated: sc.translated
                })
            }
        },

        digest: function(str) {
          var hash = 0, i, chr;
          if (str.length === 0) return hash;
          for (i = 0; i < str.length; i++) {
            chr   = str.charCodeAt(i);
            hash  = ((hash << 5) - hash) + chr;
            hash |= 0; // Convert to 32bit integer
          }
          return hash > 0 ? hash.toString(16) : (-hash).toString(16);
        },

        addScript: async function (content) {
            const newId = this.digest(content)
            if (!this.scripts[newId]) {
                this.$set(this.scripts, newId, {
                    id: newId,
                    status: 'pending',
                    content: content
                })
                await this.connector.sendScriptBackend(newId, content)
            }
            return newId
        },

        handleUpdate: async function(result) {
            console.log("In handleUpdate " + JSON.stringify(result))
            const data = result.translated.data
            for (var i = 0; i < data.length; i++) {
                var scriptId = data[i].id;
                var script = this.scripts[scriptId]
                if (data[i].translated) {
                    script.translated = data[i].translated
                    script.status = 'translated'
                    this.$set(this.scripts, scriptId, script)
                    this.jumpTo = scriptId
                    this.$emit('new-translation')
                }
            }
        },

        queryForUpdates: async function() {
            if (this.pendingScripts.length > 0) {
                console.log("Querying for updates")
                const resp = await this.connector.getTranslated(this.pendingScripts.map(s => s.id.toString()))
                console.log("Received query result")
                await this.handleUpdate({
                    translated: resp
                })
            }
        },
    },

    mounted: async function () {
        this.connector = OnLineConnector
        await this.fetchScripts();
        this.updateInterval = setInterval(async function() {
            await this.queryForUpdates()
        }.bind(this), 3000);
    }
}
</script>
