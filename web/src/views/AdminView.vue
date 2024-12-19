<script setup>
import { useDataStore } from '../DataStore';
import { onMounted, ref } from 'vue';
import { AWS } from '../AWS';
import ProjectManagementView from './AdminSubViews/ProjectManagementView.vue';
import UserManagementView from './AdminSubViews/UserManagementView.vue';

const store = useDataStore();

function switchTab(tab) {
    console.log('* switch tab:', tab);
    store.admin.current_tab = tab;
}

async function onClickConnect() {
    console.log('* connect admin endpoint');
    AWS.init({
        endpoint: store.admin.endpoint, 
        x_token: store.admin.secret_key
    });
    
    // save the endpoint to local storage
    localStorage.setItem('admin_endpoint', store.admin.endpoint);

    // send test request
    try {
        let data = await AWS.test();
        console.log('data:', data);
        store.msg('Connected to the admin APIs.');
    } catch (error) {
        console.log('error:', error);
        store.msg('Failed to connect to the admin APIs.', 'Error', 'error');
    }
}

///////////////////////////////////////////////////////////
// Help
///////////////////////////////////////////////////////////
onMounted(() => {
    console.log('* mounted AdminView');

    // load admin endpoint from local storage
    let endpoint = localStorage.getItem('admin_endpoint');
    if (endpoint != null) {
        store.admin.endpoint = endpoint;
    }
});

</script>

<template>
<div class="menu">
    <div class="menu-group">
        <div class="menu-group-box">
            <div class="flex flex-col ml-2">
                <label for="" class="text-sm">
                    <i class="fa fa-server"></i>
                    Endpoint
                </label>
                <InputText placeholder="Endpoint"
                    v-tooltip.bottom="'Endpoint for accessing admin APIs.'"
                    v-model="store.admin.endpoint" />
            </div> 
            <div class="flex flex-col ml-2">
                <label for="" class="text-sm">
                    <i class="fa fa-key"></i>
                    Secret Key
                </label>
                <InputText placeholder="Secret Key"
                    v-tooltip.bottom="'Secret key for accessing admin APIs.'"
                    v-model="store.admin.secret_key" />
            </div>
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Connect to the admin APIs.'"
                @click="onClickConnect">
                <i class="fa-solid fa-satellite-dish menu-icon"></i>
                <span>
                    Connect
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Secret Key
        </div>
    </div>

    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Manage users.'"
                @click="switchTab('user')">
                <i class="fa-solid fa-users menu-icon"></i>
                <span>
                    Users
                </span>
            </Button>
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Manage projects'"
                @click="switchTab('project')">
                <i class="fa-solid fa-suitcase menu-icon"></i>
                <span>
                    Projects
                </span>
            </Button>
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Manage CDE indexes.'"
                @click="switchTab('cde_index')">
                <i class="fa-solid fa-server menu-icon"></i>
                <span>
                    CDE Indexes
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Management
        </div>
    </div>

    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Show the user manual in a new window.'"
                @click="store.showGuide()">
                <i class="fa-solid fa-book menu-icon"></i>
                <span>
                    How-to Guide
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Help
        </div>
    </div>

</div>


<div class="main">

<!-- user management -->
<UserManagementView v-if="store.admin.current_tab == 'user'" />

<!-- project management -->
<ProjectManagementView v-if="store.admin.current_tab == 'project'" />

</div>


</template>

<style scoped>
</style>