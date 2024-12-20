import axios from "axios";

/**
 * Jimin's web service
 */
export const Jimin = {

    init: function ({endpoint}) {
        this.axios_instance = axios.create({
            baseURL: endpoint,
            timeout: 60 * 1000,
            withCredentials: true,
            headers: {}
        });
    },

    login: async function (email, password) {
        console.log('* login as ' + email);

        const rsp = await this.axios_instance.post(
            '/login', 
            {
                email: email,
                password: password
            }
        );
        // console.log(rsp.data);
        
        return rsp.data;
    },

    logout: async function () {
        console.log('* logout');

        const rsp = await this.axios_instance.post(
            '/logout'
        );
        // console.log(rsp.data);
        
        return rsp.data;
    },

    me: async function () {
        console.log('* get me');

        const rsp = await this.axios_instance.get(
            '/me'
        );
        // console.log(rsp.data);

        return rsp.data;
    },

    refreshToken: async function () {
        console.log('* refresh token');

        const rsp = await this.axios_instance.post(
            '/refresh_token'
        );

        return rsp.data;
    },

    ///////////////////////////////////////////////////////
    // General related
    ///////////////////////////////////////////////////////
    getStats: async function() {
        console.log('* get stats');

        const rsp = await this.axios_instance.get(
            '/get_stats'
        );

        return rsp.data;
    },

    ///////////////////////////////////////////////////////
    // Project related
    ///////////////////////////////////////////////////////
    getProject: async function(project_id) {
        console.log('* get project');

        const rsp = await this.axios_instance.get(
            '/get_project',
            {
                params: {
                    project_id: project_id
                }
            }
        );

        if (rsp.data.success === false) {
            return [];
        }

        return rsp.data;
    },

    getProjects: async function() {
        console.log('* get projects');

        const rsp = await this.axios_instance.get(
            '/get_projects'
        );

        if (rsp.data.success === false) {
            return [];
        }

        return rsp.data;
    },

    createProject: async function (project) {
        console.log('* create project', project);

        const rsp = await this.axios_instance.post(
            '/create_project',
            project
        );

        return rsp.data.project;
    },

    deleteProject: async function (project_id) {
        console.log('* delete project', project_id);

        const rsp = await this.axios_instance.post(
            '/delete_project',
            { project_id: project_id }
        );

        return rsp.data;
    },

    addUserToProjectByEmail: async function (project_id, email, role='member') {
        console.log('* add user to project by email', project_id, email);

        const rsp = await this.axios_instance.post(
            '/add_user_to_project_by_email',
            { 
                project_id: project_id, 
                email: email,
                role: role
            }
        );

        return rsp.data;
    },

    ///////////////////////////////////////////////////////
    // File related
    ///////////////////////////////////////////////////////
    uploadFile: async function (file) {
        console.log('* upload file', file);

        const rsp = await this.axios_instance.post(
            '/upload_file', 
            file
        );

        return rsp.data;
    },

    getFilesByProject: async function (project_id) {
        console.log('* get files by project', project_id);

        const rsp = await this.axios_instance.get(
            '/get_files_by_project',
            {
                params: {
                    project_id: project_id
                }
            }
        );

        return rsp.data.files;
    },

    updateFile: async function (file) {
        console.log('* update file', file);

        const rsp = await this.axios_instance.post(
            '/update_file',
            file
        );

        return rsp.data;
    },

    deleteFile: async function (file_id) {
        console.log('* delete file', file_id);

        const rsp = await this.axios_instance.post(
            '/delete_file',
            { file_id: file_id }
        );

        return rsp.data;
    },

    moveFile: async function (file_id, project_id) {
        console.log('* move file', file_id, project_id);

        const rsp = await this.axios_instance.post(
            '/move_file',
            { file_id: file_id, project_id: project_id }
        );

        return rsp.data;
    },

    saveFile: async function (file_id) {
        console.log('* save file', file_id);

        const rsp = await this.axios_instance.get(
            '/save_file',
            {
                params: {
                    file_id: file_id,
                }
            }
        );

        return rsp.data;
    },

    ///////////////////////////////////////////////////////
    // Concepts related
    ///////////////////////////////////////////////////////
    getConceptsByFile: async function (file_id) {
        console.log('* get concepts by file', file_id);

        const rsp = await this.axios_instance.get(
            '/get_concepts_by_file',
            {
                params: {
                    file_id: file_id
                }
            }
        );

        return rsp.data;
    },



    ///////////////////////////////////////////////////////
    // Mapping related
    ///////////////////////////////////////////////////////
    getSources: async function () {
        console.log('* get sources');

        const rsp = await this.axios_instance.get(
            '/get_sources'
        );

        return rsp.data.sources;
    },

    getCollectionsBySource: async function (source) {
        console.log('* get collections by source', source);

        const rsp = await this.axios_instance.get(
            '/get_collections_by_source',
            {
                params: {
                    source: source
                }
            }
        );

        return rsp.data.collections;
    },

    /**
     * Search for the terms in the source and collections
     * 
     * @param {string} source Elasticsearch index name
     * @param {list} collections List of collection names
     * @param {object} queries List of query objects
     * @param {int} size Number of results to return
     * @param {boolean} flag_openai Flag to use OpenAI for query expansion
     * @param {boolean} flag_fuzzy Flag to use fuzzy search
     * @returns 
     */
    search: async function (
        source, 
        collections, 
        queries, 
        flag_embedding=false,
        flag_openai=false, 
        flag_fuzzy=true,
        size=100, 
    ) {
        console.log('* search', source, collections, queries);

        const rsp = await this.axios_instance.post(
            '/search',
            {
                source: source,
                collections: collections,
                queries: queries,
                flag_embedding: flag_embedding,
                flag_openai: flag_openai,
                flag_fuzzy: flag_fuzzy,
                size: size,
            }
        );

        return rsp.data.results;
    },

    async updateSelectedResults(concept_id, selected_results) {
        console.log('* update selected results', concept_id, selected_results);

        const rsp = await this.axios_instance.post(
            '/update_selected_results',
            {
                concept_id: concept_id,
                selected_results: selected_results
            }
        );

        return rsp.data;
    },

    async getMapping(concept_id) {
        console.log('* get mapping', concept_id);

        const rsp = await this.axios_instance.get(
            '/get_mapping',
            {
                params: {
                    concept_id: concept_id
                }
            }
        );

        return rsp.data.mapping;
    }
}