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
}