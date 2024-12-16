<script setup>
import { useRouter } from "vue-router";
import { useDataStore } from "../DataStore";
import { onMounted, ref } from "vue";
const store = useDataStore();
const router = useRouter();

function onClickGoHome() {
    router.push('/');
}
</script>

<template>
<div id="navi">
    <div class="navi-left prevent-select">
        <div class="navi-item home"
            @click="onClickGoHome"
            :class="{'active-page': store.current_view=='homepage'}">
            <i class="fa fa-home"></i>
            Home
        </div>
        <div class="navi-item"
            @click="store.changeView('dashboard')"
            :class="{'active-page': store.current_view=='dashboard'}">
            <i class="fa fa-dashboard"></i>
            Dashboard
        </div>
        <div class="navi-item"
            @click="store.changeView('profile')"
            :class="{'active-page': store.current_view=='profile'}">
            <i class="fa-regular fa-user"></i>
            My Profile
        </div>
        <div class="navi-item"
            @click="store.changeView('project_list')"
            :class="{'active-page': store.current_view=='project_list'}">
            <i class="fa-solid fa-briefcase"></i>
            Projects
        </div>
        <div class="navi-item"
            @click="store.changeView('mapping')"
            :class="{'active-page': store.current_view=='mapping'}">
            <i class="fa-solid fa-arrows-left-right-to-line"></i>
            Mapping
        </div>
        <div class="navi-item"
            @click="store.changeView('review')"
            :class="{'active-page': store.current_view=='review'}">
            <i class="fa-solid fa-code-compare"></i>
            Review
        </div>
        <!-- <div class="navi-item"
            @click="store.changeView('create')"
            :class="{'active-page': store.current_view=='create'}">
            <i class="fa-regular fa-pen-to-square"></i>
            Create CDE
        </div> -->
        <div class="navi-item"
            @click="store.changeView('vis')"
            :class="{'active-page': store.current_view=='vis'}">
            <i class="fa-brands fa-uncharted"></i>
            Visualization
        </div>
    </div>

    <div class="navi-right">

        <div class="mr-2">
            <i class="fa-solid fa-clipboard-list mr-1"></i>
            <span class="italic">
                {{ store.project.name }}
            </span>
        </div>

        <Divider layout="vertical"/>

        <div>
            <i class="fa-solid fa-user mr-1"></i>
            <span>
                {{ store.user.name }}
            </span>
            ,
            <span>
                logout
            </span>
        </div>
    </div>
</div>
</template>

<style scoped>
#navi {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
    height: 2.5rem;
}
.navi-left {
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
}
.navi-right {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-end;
    padding: 0 0.5rem 0 0;
}
.navi-item {
    margin-right: 0.5rem;
    padding: 0.5rem 1rem;
    border: 1px solid transparent;
    border-bottom: 0;
    text-align: center;
    cursor: pointer;
}
.navi-item:hover {
    background-color: var(--bg-color-menu-hover);
}
.navi-item.active-page {
    font-weight: bold;
    border: 1px solid var(--bd-color);
    border-bottom: 0;
    background-color: var(--bg-color-menu);

    /* offset for merging to the menu */
    position: relative;
    bottom: -1px;
}
.home {
    color: white;
    background: #2c4fa6;
}
.home:hover {
    background: #26448f;
}
</style>