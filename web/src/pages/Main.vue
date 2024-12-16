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
const store = useDataStore();

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

<!-- Review view -->
<ReviewView v-if="store.current_view == 'review'" />

<!-- Vis view -->
<VisView v-if="store.current_view == 'vis'" />
</div>

<Footer />

</template>

<style scoped>
</style>