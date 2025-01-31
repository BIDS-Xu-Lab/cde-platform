<script setup>
import NaviMenu from '../components/NaviMenu.vue';
import DashboardView from '../views/DashboardView.vue';
import MappingView from '../views/MappingView.vue';
import ProfileView from '../views/ProfileView.vue';
import Footer from '../components/Footer.vue';

import { useDataStore } from '../DataStore';
import ProjectListView from '../views/ProjectListView.vue';
import ReviewView from '../views/ReviewView.vue';
import VisView from '../views/VisView.vue';
import TeamView from '../views/TeamView.vue';
import SettingView from '../views/SettingView.vue';
import GrantReviewView from '../views/GrantReviewView.vue';
import AdminView from '../views/AdminView.vue';

import { onMounted } from 'vue';
import { Jimin } from '../Jimin';

const store = useDataStore();

onMounted(() => {
    console.log('* mounted Main');

    if (store.isLoggedIn()) {

    } else {
        // send a request to server to check if the user is still logged in
        try {
            Jimin.me().then((data) => {
                store.setUser(data.user);
                store.startRefreshToken();
            }).catch((error) => {
                console.log('error:', error);
                store.gotoLogin();
            });
        } catch (error) {
            console.log('error:', error);
            store.gotoLogin();
        }
    }
});

</script>
<template>
<!-- Navigation menu -->
<NaviMenu />

<!-- Main content -->
<div id="main"
    v-if="store.user != null">

<!-- Dashboard view -->
<DashboardView v-if="store.current_view == 'dashboard'" />

<!-- Mapping view -->
<MappingView v-if="store.current_view == 'mapping'" />

<!-- Profile view -->
<ProfileView v-if="store.current_view == 'profile'" />

<!-- Project list view -->
<ProjectListView v-if="store.current_view == 'project_list'" />

<!-- Team view -->
<TeamView v-if="store.current_view == 'team'" />

<!-- Review view -->
<ReviewView v-if="store.current_view == 'review'" />

<!-- Vis view -->
<VisView v-if="store.current_view == 'vis'" />

<!-- Setting view -->
<SettingView v-if="store.current_view == 'setting'" />

<!-- Grant review view -->
<GrantReviewView v-if="store.current_view == 'grant_review'" />

<!-- Admin view -->
<AdminView v-if="store.current_view == 'admin' && store.user?.role == 'admin'" />

</div>

<Footer />

</template>

<style scoped>
</style>