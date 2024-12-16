import { defineStore } from 'pinia';
import { useToast } from "primevue/usetoast";

export const useDataStore = defineStore('jarvis', {

state: () => ({
    version: '0.7.2',

    // current user
    user: {
        id: 1,
        name: 'Luke Skywalker',
        role: 'admin',
        email: "luke.skywalker@yale.edu"
    },

    // current current_view
    current_view: 'dashboard',

    // working project
    project: {
        id: 1,
        name: 'My Project',
        description: 'This is a project description',
        created: '2021-06-01',
    },

    // working file
    file: [],

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

        working_term_idx: -1,

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
}),

getters: {
    
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
    }
}
});