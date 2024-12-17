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
    // Project related
    ///////////////////////////////////////////////////////
    getProjects: async function() {
        console.log('* get projects');

        const rsp = await this.axios_instance.get(
            '/get_projects'
        );

        if (rsp.data.success === false) {
            return [];
        }

        return rsp.data.projects;
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
    }
}