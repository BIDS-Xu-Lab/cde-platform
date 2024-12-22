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

    // statistics for dashboard
    // {
    //     n_projects: 0,
    //     n_files: 0,
    //     n_concepts: 0,
    //     n_mappings: 0,
    // },
    stats: null,

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

    // working file for mapping or other tasks
    working_file: null,

    // all the concepts in the current working file
    working_file_concepts: [],

    // working concept
    working_concept: null,

    // working mappings
    // {
    //     concept_id: {
    //         selected_results: [],
    //         search_results: [],
    //     }
    // }
    working_mappings: {},

    // for mapping
    mapping: {
        sources: [],
        collections: [],

        selected_source: null,
        selected_collections: [],

        // for the terms filtering and sorting
        sort_terms_by: null, // it's a string, e.g., name|asc
        filter_terms_by: '',

        // for the results filtering and sorting
        filter_results_by: '',
        sort_results_by: null,
        sort_results_order_by: null,

        // mapping row data columns
        data_col_term: '',
        data_col_description: '',
        data_col_value: '',
    },

    // for admin only
    admin: {
        current_tab: '',
        endpoint: '',
        secret_key: '',
        users: [],
        projects: [],
    },

    // system features for users
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
    working_mappings_search_results_without_selected(state) {
        if (!state.working_concept) {
            return [];
        }

        return state.working_mappings[state.working_concept.concept_id]?.search_results.filter(r => !state.working_mappings[state.working_concept.concept_id].selected_results.includes(r));
    },

    filtered_working_file_concepts(state) {
        if (!state.working_file_concepts) {
            return [];
        }

        let filtered_sorted_concepts = []
        // if the filter_term is empty string after trim, just return all the concepts
        if (state.mapping.filter_terms_by.trim() == '') {
            filtered_sorted_concepts = state.working_file_concepts;
        }

        // filter
        filtered_sorted_concepts = state.working_file_concepts.filter(c => {
            let flag_has_keyword = c.term.toLowerCase().includes(state.mapping.filter_terms_by.toLowerCase());

            return flag_has_keyword;
        });

        // order by the given column
        if (state.mapping.sort_terms_by) {
            let [sort_by, order_by] = state.mapping.sort_terms_by.split('|');
            let sort_func = (a, b) => {
                if (order_by == 'asc') {
                    return a[sort_by] > b[sort_by] ? 1 : -1;
                } else {
                    return a[sort_by] < b[sort_by] ? 1 : -1;
                }
            };

            filtered_sorted_concepts.sort(sort_func);
        }

        return filtered_sorted_concepts;
    },

    n_mapped_concepts_in_working_file(state) {
        return state.working_file_concepts.filter(c => state.hasSelectedResults(c)).length;
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
            try {
                await Jimin.refreshToken();
            } catch (error) {
                console.log('Error refreshing token:', error);
                this.msg('Error refreshing token', 'Error', 'error');

                // logout the user
                this.logout();
            }
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
    // Project File
    ///////////////////////////////////////////////////////
    async updateCurrentProjectFiles() {
        // get all files for this project
        let files = await Jimin.getFilesByProject(
            store.current_project.project_id
        );
        console.log('* got project files:', files);
        store.files = files;
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
    isWorkingConcept(concept) {
        // check if the term is the working term by indexOf
        // working file is a list of term objects, need to use id to compare
        return this.working_concept?.id == concept.id;
    },

    clearMappingData() { 
        this.working_file = null;
        this.working_concept = null;
        this.working_file_concepts = [];
        this.working_mappings = {};
    },

    addSelectedResultToWorkingConcept(result) {
        if (!this.working_concept) {
            return;
        }

        if (!this.working_mappings[this.working_concept.concept_id]) {
            return;
        }

        // if the result is already in the selected results, skip
        if (this.working_mappings[this.working_concept.concept_id].selected_results.includes(result)) {
            return;
        }

        // update the result with the values from the working concept
        result.value_mapping = {};
        this.working_concept.values.map(v => {
            result.value_mapping[v] = '';
        });

        // save the result
        this.working_mappings[this.working_concept.concept_id].selected_results.push(result);
    },

    removeSelectedResultFromWorkingConcept(result) {
        if (!this.working_concept) {
            return;
        }

        if (!this.working_mappings[this.working_concept.concept_id]) {
            return;
        }

        // remove the result
        this.working_mappings[this.working_concept.concept_id].selected_results = this.working_mappings[this.working_concept.concept_id].selected_results.filter(r => r != result);
    },

    ///////////////////////////////////////////////////////
    // User File
    ///////////////////////////////////////////////////////
    hasSelectedResults(concept) {
        if (this.working_mappings[concept.concept_id]) {
            false;
        }
        if (this.working_mappings[concept.concept_id]?.selected_results) {
            return this.working_mappings[concept.concept_id].selected_results.length > 0;
        }
        return false;
    },
    hasSearchResults(concept) {
        if (this.working_mappings[concept.concept_id]) {
            return this.working_mappings[concept.concept_id].search_results.length > 0;
        }
        return false;
    },

    getSelectedResults(concept) {
        if (this.working_mappings[concept.concept_id]) {
            return this.working_mappings[concept.concept_id].selected_results;
        }
        return [];
    }
}
});