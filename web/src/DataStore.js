import { defineStore } from 'pinia';
import { useToast } from "primevue/usetoast";
import { hasResults } from './CDEHelper';
import router from './router';
import { Jimin } from './Jimin';

export const useDataStore = defineStore('jarvis', {

state: () => ({
    version: '0.7.2',

    // current user
    // {
    //     user_id: 'aksl-123-12--123',
    //     name: 'Luke Skywalker',
    //     role: 'admin',
    //     email: "luke.skywalker@yale.edu"
    // }
    user: null,

    // current current_view
    current_view: 'dashboard',

    // working project
    working_project: {
        id: 1,
        name: 'My Project',
        description: 'This is a project description',
        created: '2021-06-01',
    },

    // working file
    working_file: [],

    // working term
    working_term_idx: -1,

    // for mapping
    mapping: {
        sources: [
            { value: "umls_train_clinical_document", name: "UMLS (Clinical Document)"},
            { value: "nih-v3-cde", name: "NIH CDE v3"},
            { value: "nih-cde", name: "NIH CDE"},
            { value: "nda-demo1-cde", name: "NDA CDE Demo 1"},
            { value: "nda-demo2-cde", name: "NDA CDE Demo 2"},
        ],
        collections: {
            "nih-cde": [
                "NINDS",
                "LOINC",
                "NHLBI",
                "PROMIS / Neuro-QOL",
                "NLM",
                "NICHD",
                "RADx-UP",
                "NIH-Endorsed",
                "NEI",
                "Project 5 (COVID-19)",
                "NCI",
                "GRDR",
                "NINR",
                "TEST",
                "Women's CRN",
                "ONC",
                "NIDA"
            ],
        },

        selected_sources: null,
        selected_collections: null,
        sort_terms_by: null,
        filter_terms_by: '',


        data_col_name: 'element',
        data_col_description: 'description',
        data_col_value: 'value',
    },

    features: {
        embedding_search: {
            enabled: false,
        },
        query_expansion: {
            enabled: false,
        },
    },

    // other system related data
    toast: useToast(),

    // for the router
    router: router,
}),

getters: {
    working_term: (state) => {
        return state.working_file[state.working_term_idx];
    },

},

actions: {
    changeView(new_view) {
        this.current_view = new_view;
    },

    showGuide() {
        this.toast.add({
            severity: 'info',
            summary: 'Guide',
            detail: 'This is a guide to the application',
            life: 5000
        });
    },

    gotoMain(new_view) {
        this.changeView(new_view);
        this.router.push('/main');
    },

    gotoLogin() {
        this.router.push('/login');
    },

    isLoggedIn() {
        return this.user != null;
    },

    startRefreshToken() {
        // refresh the token every 10 minutes
        setInterval(async () => {
            if (this.isLoggedIn()) {
                await Jimin.refreshToken();
            }
        }, 2 * 60 * 1000);
    },

    ///////////////////////////////////////////////////////
    // User File
    ///////////////////////////////////////////////////////
    setUser(user) {
        this.user = user;
    },

    async logout() {
        // send a request to the server to logout
        await Jimin.logout();

        // then clear the user
        this.user = null;

        // redirect to the login page
        this.gotoLogin();
    },

    ///////////////////////////////////////////////////////
    // Working File
    ///////////////////////////////////////////////////////
    isWorkingTerm(term) {
        // check if the term is the working term by indexOf
        // working file is a list of term objects, need to use id to compare
        return this.working_term_idx == term.id;
    },

    reset() {
        this.mapping.working_term_idx = [];
    }
}
});