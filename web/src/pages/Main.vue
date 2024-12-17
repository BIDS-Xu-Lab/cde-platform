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
const store = useDataStore();

import { onMounted } from 'vue';

onMounted(() => {
    console.log('* mounted Main');

    if (store.isLoggedIn()) {

    } else {
        store.gotoLogin();
    }
});

</script>
<template>
<!-- Navigation menu -->
<NaviMenu />

<!-- Main content -->
<div id="main">

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

</div>

<Footer />

</template>

<style scoped>
</style>