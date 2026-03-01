import { createI18n } from 'vue-i18n'
import pt from './locales/pt.json'
import en from './locales/en.json'
import es from './locales/es.json'

const messages = {
    pt,
    en,
    es
}

// Get saved language or detect browser language
const savedLocale = localStorage.getItem('poker-locale')
const browserLocale = navigator.language?.split('-')[0] || 'pt'
const defaultLocale = savedLocale || (Object.keys(messages).includes(browserLocale) ? browserLocale : 'pt')

const i18n = createI18n({
    legacy: false, // use Composition API
    locale: defaultLocale,
    fallbackLocale: 'pt',
    messages
})

export default i18n
