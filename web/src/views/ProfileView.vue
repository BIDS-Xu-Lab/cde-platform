<script setup>
import { useDataStore } from '../DataStore';
const store = useDataStore();

function onClickSave() {
    console.log('* clicked Save my profile');
}
</script>

<template>
<div class="menu">
    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.right="'Save my profile information.'"
                @click="onClickSave">
                <i class="fa-regular fa-save menu-icon"></i>
                <span>
                    Save Profile
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Profile
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

<Panel class="h-full personal-panel">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa-solid fa-user"></i>
                        Personal Information
                    </div>
                    <div class="panel-subtitle text-sm">
                    </div>
                </div>
            </div>
            <div>

            </div>
        </div>
    </template>
</Panel>


<Panel class="h-full stats-panel">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa-solid fa-briefcase"></i>
                        Statistics
                    </div>
                    <div class="panel-subtitle text-sm">
                    </div>
                </div>
            </div>
            <div>

            </div>
        </div>
    </template>
</Panel>

</div>

</template>

<style scoped>
.personal-panel {
    width: 50%;
    margin: 0 0.5rem 0 0;
}
.stats-panel {
    width: 50%;
}
</style>