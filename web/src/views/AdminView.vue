<script setup>
import { useDataStore } from '../DataStore';
import { onMounted, ref } from 'vue';
import { AWS } from '../AWS';

const store = useDataStore();

// current 
const current_tab = ref('user');

function switchTab(tab) {
    console.log('* switch tab:', tab);
    current_tab.value = tab;
}

// secret key for accessing admin APIs
const admin_endpoint = ref('');
const admin_secret_key = ref('');

async function onClickConnect() {
    console.log('* connect admin endpoint');
    AWS.init({
        endpoint: admin_endpoint.value, 
        x_token: admin_secret_key.value
    });
    
    // save the endpoint to local storage
    localStorage.setItem('admin_endpoint', admin_endpoint.value);

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
// User management
///////////////////////////////////////////////////////////
const users = ref([]);
const info_add_user = ref('');
const data_add_user = ref({
    name: '',
    email: '',
    password: ''
});
async function onClickAddUser() {
    console.log('* clicked add user');
    info_add_user.value = '';

    // check name, email, password
    if (data_add_user.value.name.trim() == '') {
        info_add_user.value = 'Name is required.';
        return;
    }

    if (data_add_user.value.email.trim() == '') {
        info_add_user.value = 'Email is required.';
        return;
    }

    if (data_add_user.value.password.trim() == '') {
        info_add_user.value = 'Password is required.';
        return;
    }

    if (data_add_user.value.password.trim().length < 8) {
        info_add_user.value = 'Password at least 8 characters.';
        return;
    }

    // add a new user
    try {
        let data = await AWS.registerUser(
            data_add_user.value.email,
            data_add_user.value.name,
            data_add_user.value.password,
        );
        console.log('data:', data);
        store.msg('Server returns: ' + data.message);

    } catch (error) {
        console.log('error:', error);
        store.msg('Failed to add a new user.', 'Error', 'error');
    }
}

function onClickGeneratePassword() {
    console.log('* clicked generate password');

    // generate a random character password
    let password = '';
    let characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let charactersLength = characters.length;
    for (let i = 0; i < 8; i++) {
        password += characters.charAt(Math.floor(Math.random() * charactersLength));
    }

    data_add_user.value.password = password;
}

async function onClickRefreshUserList() {
    console.log('* clicked refresh user list');

    // get user list
    try {
        let data = await AWS.getAllUsers();
        console.log('data:', data);
        store.msg('Server returns: ' + data.message);

        users.value = data.users;

    } catch (error) {
        console.log('error:', error);
        store.msg('Failed to get user list.', 'Error', 'error');
    }
}

function onClickClearDataAddUser() {
    console.log('* clicked clear data add user');
    data_add_user.value = {
        name: '',
        email: '',
        password: ''
    };
    info_add_user.value = '';
}
///////////////////////////////////////////////////////////
// Project management
///////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////
// Help
///////////////////////////////////////////////////////////
onMounted(() => {
    console.log('* mounted AdminView');

    // load admin endpoint from local storage
    let endpoint = localStorage.getItem('admin_endpoint');
    if (endpoint != null) {
        admin_endpoint.value = endpoint;
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
                    v-model="admin_endpoint" />
            </div> 
            <div class="flex flex-col ml-2">
                <label for="" class="text-sm">
                    <i class="fa fa-key"></i>
                    Secret Key
                </label>
                <InputText placeholder="Secret Key"
                    v-tooltip.bottom="'Secret key for accessing admin APIs.'"
                    v-model="admin_secret_key" />
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
                    User Management
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            User
        </div>
    </div>

    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Manage projects'"
                @click="switchTab('project')">
                <i class="fa-solid fa-suitcase menu-icon"></i>
                <span>
                    Project Management
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Project
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

<div v-if="current_tab == 'user'" class="h-full w-full flex flex-row">
    
    <div class="w-1/3 mr-1">
        <Panel>
            <template #header>
                <div class="w-full flex justify-between">
                    <div class="flex">
                        <div class="flex-col">
                            <div class="text-lg font-bold">
                                <i class="fa-solid fa-user-plus"></i>
                                Quick Add User
                            </div>
                            <div class="panel-subtitle text-sm">
                            </div>
                        </div>
                    </div>
                    <div>

                    </div>
                </div>
            </template>

            <div class="flex flex-col items-center">
                <div class="flex flex-col w-full mr-1 mb-2">
                    <label class="text-sm" for="">Name</label>
                    <InputText placeholder="Name" 
                        v-model="data_add_user.name" />
                </div>
                <div class="flex flex-col w-full mr-1 mb-2">
                    <label class="text-sm" for="">Email</label>
                    <InputText placeholder="Email"
                        v-model="data_add_user.email" />
                </div>
                <div class="flex flex-col w-full mr-1 mb-2">
                    <label class="text-sm" for="">Password</label>
                    <div class="flex flex-row">
                        <Button severity="secondary"
                                class="mr-2"
                                v-tooltip.bottom="'Generate a random password.'"
                                @click="onClickGeneratePassword">
                                <i class="fa-solid fa-key"></i>
                            </Button>
                        <InputText placeholder="Password"
                            class="flex-grow"
                            v-model="data_add_user.password" />
                    </div>
                </div>

                <div class="flex flex-col mr-1">
                    <div class="text-sm text-red-500">
                        {{ info_add_user }}
                    </div>
                    <div class="flex flex-row justify-between">
                        <div class="mr-2">
                            <Button
                                v-tooltip.bottom="'Clear all info.'"
                                @click="onClickClearDataAddUser">
                                <i class="fa-solid fa-times"></i>
                                <span>
                                    Clear
                                </span>
                            </Button>
                        </div>

                        <div>
                            <Button
                                v-tooltip.bottom="'Add a new user.'"
                                @click="onClickAddUser">
                                <i class="fa-solid fa-user-plus"></i>
                                <span>
                                    Add User
                                </span>
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </Panel>
    </div>

    <Panel class="w-2/3">
        <template #header>
            <div class="w-full flex justify-start">
                <div class="flex mr-2">
                    <div class="flex-col">
                        <div class="text-lg font-bold">
                            <i class="fa-solid fa-users"></i>
                            User List
                        </div>
                        <div class="panel-subtitle text-sm">
                        </div>
                    </div>
                </div>
                <div>
                    <Button 
                        size="small"
                        v-tooltip.bottom="'Update user list.'"
                        @click="onClickRefreshUserList">
                        <i class="fa-solid fa-sync"></i>
                        Refresh List
                    </Button>
                </div>
            </div>
        </template>

        <div>
            <DataTable :value="users" paginator 
                :rows="10" 
                :rowsPerPageOptions="[10, 20, 50]" 
                tableStyle="min-width: 50rem">
                <template #empty> No users found. </template>
                <Column field="name" header="Name" style="width: 25%"></Column>
                <Column field="email" header="Email" style="width: 25%"></Column>
                <Column field="role" header="Role" style="width: 25%"></Column>
                <Column header="Actions" style="width: 25%">
                
                </Column>
            </DataTable>
        </div>
    </Panel>
    
</div>

</div>


</template>

<style scoped>
</style>