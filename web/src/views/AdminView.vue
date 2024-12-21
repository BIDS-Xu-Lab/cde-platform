<script setup>
import { useDataStore } from '../DataStore';
import { onMounted, ref } from 'vue';
import { AWS } from '../AWS';
import ProjectManagementView from './AdminSubViews/ProjectManagementView.vue';
import UserManagementView from './AdminSubViews/UserManagementView.vue';
import MongoManagementView from './AdminSubViews/MongoManagementView.vue';
import CDEIndexManagementView from './AdminSubViews/CDEIndexManagementView.vue';

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
                    <font-awesome-icon :icon="['fa', 'server']" />
                    Endpoint
                </label>
                <InputText placeholder="Endpoint"
                    v-tooltip.bottom="'Endpoint for accessing admin APIs.'"
                    v-model="store.admin.endpoint" />
            </div> 
            <div class="flex flex-col ml-2">
                <label for="" class="text-sm">
                    <font-awesome-icon :icon="['fa', 'key']" />
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
                <font-awesome-icon :icon="['fas', 'satellite-dish']" class="menu-icon" />
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
                <font-awesome-icon :icon="['fas', 'users']" class="menu-icon" />
                <span>
                    Users
                </span>
            </Button>
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Manage projects'"
                @click="switchTab('project')">
                <font-awesome-icon :icon="['fas', 'suitcase']" class="menu-icon" />
                <span>
                    Projects
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
                v-tooltip.bottom="'Manage CDE indexes.'"
                @click="switchTab('mongo')">
                <font-awesome-icon :icon="['fas', 'database']" class="menu-icon" />
                <span>
                    MongoDB
                </span>
            </Button>
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Manage CDE indexes.'"
                @click="switchTab('cde_index')">
                <font-awesome-icon :icon="['fas', 'server']" class="menu-icon" />
                <span>
                    CDE Indexes
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Databases
        </div>
    </div>

    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Show the user manual in a new window.'"
                @click="store.showGuide()">
                <font-awesome-icon :icon="['fas', 'book']" class="menu-icon" />
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
<UserManagementView v-show="store.admin.current_tab == 'user'" />

<!-- project management -->
<ProjectManagementView v-show="store.admin.current_tab == 'project'" />

<!-- mongodb management -->
<MongoManagementView v-show="store.admin.current_tab == 'mongo'" />

<!-- cde index management -->
<CDEIndexManagementView v-show="store.admin.current_tab == 'cde_index'" />

</div>
</template>

<style scoped>
</style>