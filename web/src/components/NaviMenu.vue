<script setup>
import { useRouter } from "vue-router";
import { useDataStore } from "../DataStore";
import { onMounted, ref } from "vue";
const store = useDataStore();
const router = useRouter();

function onClickGoHome() {
    router.push('/');
}

onMounted(() => {
    console.log('* mounted Footer');
});
</script>

<template>
<div id="navi"
    v-if="store.user != null">
    <div class="navi-left prevent-select">
        <div class="navi-item home"
            @click="onClickGoHome"
            :class="{'active-page': store.current_view=='homepage'}">
            <font-awesome-icon :icon="['fa', 'home']" />
            Home
        </div>
        <div class="navi-item"
            @click="store.changeView('dashboard')"
            :class="{'active-page': store.current_view=='dashboard'}">
            <font-awesome-icon :icon="['fa', 'dashboard']" />
            Dashboard
        </div>
        <div class="navi-item"
            @click="store.changeView('project_list')"
            :class="{'active-page': store.current_view=='project_list'}">
            <font-awesome-icon :icon="['fas', 'briefcase']" />
            Projects
        </div>

        <!-- functions after login -->
        <div v-show="store.working_file != null && store.working_file?.round[store.working_file?.round.length - 1]?.stage == 'mapping'"
            class="navi-item"
            @click="store.changeView('mapping')"
            :class="{'active-page': store.current_view=='mapping'}">
            <font-awesome-icon :icon="['fa-solid', 'arrows-left-right-to-line']" />
            Mapping
        </div>
        <div v-show="store.working_file != null && store.working_file?.round[store.working_file?.round.length - 1]?.stage == 'reviewing'" 
            class="navi-item"
            @click="store.changeView('review')"
            :class="{'active-page': store.current_view=='review'}">
            <font-awesome-icon :icon="['fa-solid', 'code-compare']" />
            Review
        </div>
        <!-- <div class="navi-item"
            @click="store.changeView('create')"
            :class="{'active-page': store.current_view=='create'}">
            <font-awesome-icon :icon="['fa-regular', 'pen-to-square']" />
            Create CDE
        </div> -->
        <!-- <div class="navi-item"
            @click="store.changeView('vis')"
            :class="{'active-page': store.current_view=='vis'}">
            <font-awesome-icon :icon="['fab', 'uncharted']" />
            Visualization
        </div>
        <div class="navi-item"
            @click="store.changeView('profile')"
            :class="{'active-page': store.current_view=='profile'}">
            <font-awesome-icon :icon="['fa-regular', 'user']" />
            My Profile
        </div>
        <div class="navi-item"
            @click="store.changeView('setting')"
            :class="{'active-page': store.current_view=='setting'}">
            <font-awesome-icon :icon="['fa-solid', 'gears']" />
            Settings
        </div> -->
        <div v-show="store.user?.role == 'admin'" 
            class="navi-item"
            @click="store.changeView('admin')"
            :class="{'active-page': store.current_view=='admin'}">
            <font-awesome-icon :icon="['fab', 'battle-net']" />
            Admin
        </div>
    </div>

    <div class="navi-right">

        <div>
            <template v-if="store.working_project != null">
                <font-awesome-icon :icon="['fas', 'briefcase']" class="mr-1" />
                <span class="italic">
                    {{ store.working_project?.name }}
                </span>
                - 
                <font-awesome-icon :icon="['fa', 'file']" class="mr-1" />
                <span class="italic">
                    {{ store.working_file?.filename }}
                </span>
                - 
                <font-awesome-icon :icon="['fab', 'sourcetree']" class="mr-1"/>
                <span class="italic">
                    {{ store.working_file?.round[store.working_file?.round.length - 1]?.stage }}
                </span>
            </template>
        </div>

        <Divider layout="vertical"/>

        <div v-if="store.user == null">
            <font-awesome-icon :icon="['far', 'user']" class="mr-1" />
            <span @click="store.gotoLogin()">
                Login
            </span>
        </div>
        <div v-else>
            <font-awesome-icon :icon="['fas', 'user']" class="mr-1" />
            <span>
                {{ store.user.name }}
            </span>
            <span>
                <Button label="Logout" variant="link" @click="store.logout();" />
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