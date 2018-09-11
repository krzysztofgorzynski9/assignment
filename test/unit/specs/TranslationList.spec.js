import Vue from 'vue'
import sinon from 'sinon'
import { shallowMount } from '@vue/test-utils'
import TranslationList from '@/components/TranslationList'

describe('TranslationList.vue', () => {
    it('should accumulates entries', async () => {
        const c = shallowMount(TranslationList)
        c.vm.connector.sendScriptBackend = sinon.stub()
        c.vm.connector.sendScriptBackend.resolves(0)
        await c.vm.addScript('Tudo mundo danca')
        expect(c.vm.pendingScripts.length).to.equal(1)
        c.vm.connector.sendScriptBackend.resolves(1)
        await c.vm.addScript('Tudo mundo canta')
        expect(c.vm.pendingScripts.length).to.equal(2)
    })

    it('should place untranslated messages at the end', async () => {
        const c = shallowMount(TranslationList)
        c.vm.connector.sendScriptBackend = sinon.stub()
        c.vm.connector.sendScriptBackend.resolves('0')
        const sId1 = await c.vm.addScript('Open the textbook at page 52.')
        c.vm.connector.sendScriptBackend.resolves('1')
        const sId2 = await c.vm.addScript('Let\'s go to the cinema.')
        expect(c.vm.pendingScripts[0].id).to.equal(sId1)
        expect(c.vm.pendingScripts[1].id).to.equal(sId2)
    })

    it('should sort scripts by length of the translated message', async () => {
        const c = shallowMount(TranslationList)
        c.vm.connector.sendScriptBackend = sinon.stub()
        c.vm.connector.sendScriptBackend.resolves('0')
        const s1Id = await c.vm.addScript('Tudo mundo danca. Tudo mundo canta.')
        c.vm.connector.sendScriptBackend.resolves('1')
        const s2Id = await c.vm.addScript('Passei no vestibular')
        c.vm.connector.getScript = sinon.stub()
        c.vm.connector.getScript.onFirstCall().resolves({translated: 'Translated msg longer'})
        c.vm.connector.getScript.onSecondCall().resolves({translated: 'Translated msg'})
        await c.vm.handleUpdate({'status': 'ok', 'translated': [s1Id, s2Id]})
        expect(c.vm.translatedScripts[0].id).to.equal(s2Id)
    })
})
