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
    current_view: 'project_list',

    // all projects belong to the current user
    projects: [],

    // all files belong to the selected project
    files: [],

    // working project
    working_project: null,
    // {
    //     id: 1,
    //     name: 'My Project',
    //     description: 'This is a project description',
    //     created: '2021-06-01',
    // },

    // working file
    working_file: null,

    // working file
    working_file_concepts: [],

    // working term
    working_term_idx: -1,

    // for mapping
    mapping: {
        sources: [],
        collections: [],

        selected_source: null,
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
        console.log('* start refreshing token');
        // refresh the token every 10 minutes
        setInterval(async () => {
            Jimin.refreshToken();
        }, 3 * 60 * 1000);
    },

    msg(message, title='Message', type='info') {
        this.toast.add({
            severity: type,
            summary: title,
            detail: message,
            life: 3000
        });
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
    isWorkingConcept(term) {
        // check if the term is the working term by indexOf
        // working file is a list of term objects, need to use id to compare
        return this.working_term_idx == term.id;
    },

    reset() {
        this.mapping.working_term_idx = [];
    }
}
});