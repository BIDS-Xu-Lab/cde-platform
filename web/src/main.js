import "primeicons/primeicons.css";
import './style.css';

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import Aura from '@primevue/themes/aura';
import { createPinia } from 'pinia';
import { useDataStore } from "./DataStore";
import { definePreset } from '@primevue/themes';
import Tooltip from 'primevue/tooltip';
import * as CDEHelper from './CDEHelper';
import { theme } from './theme';

// create the app
const app = createApp(App)

// add the ToastService to the app
app.use(ToastService);

// add pinia to the app
const pinia = createPinia()
app.use(pinia);

// bind the store to the window object
const store = useDataStore();
window.store = store;

// make sample data
store.file = CDEHelper.makeSampleData();

// add the router to the app
app.use(router);

// add PrimeVue to the app
const my_theme = definePreset(Aura, theme);

app.use(PrimeVue, {
    theme: {
        preset: my_theme,
    }
});

// add the Tooltip directive to the app
app.directive('tooltip', Tooltip);

// mount the app to the DOM
app.mount('#app')
