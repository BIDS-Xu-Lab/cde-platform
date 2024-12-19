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
}