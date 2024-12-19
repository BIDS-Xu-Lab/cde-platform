import axios from "axios";

/**
 * Admin's Web Service
 */
export const AWS = {

    init: function ({endpoint, x_token}) {
        this.axios_instance = axios.create({
            baseURL: endpoint,
            timeout: 60 * 1000,
            withCredentials: true,
            headers: {
                'x-token': x_token
            }
        });
    },

    test: async function () {
        console.log('* test admin connection');

        const rsp = await this.axios_instance.get(
            '/test'
        );
        
        return rsp.data;
    },

    registerUser: async function (email, name, password, role='user') {
        console.log('* register user ' + email);

        const rsp = await this.axios_instance.post(
            '/register_user',
            {
                email: email,
                name: name,
                role: role,
                password: password
            }
        );
        
        return rsp.data;
    },

    getAllUsers: async function () {
        console.log('* get all users');

        const rsp = await this.axios_instance.get(
            '/get_all_users'
        );
        
        return rsp.data;
    },

    getAllProjects: async function () {
        console.log('* get all projects');

        const rsp = await this.axios_instance.get(
            '/get_all_projects'
        );
        
        return rsp.data;
    },
}