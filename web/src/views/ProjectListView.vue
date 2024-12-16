<script setup>
import { useDataStore } from '../DataStore';
const store = useDataStore();

function onClickSave() {
    console.log('* clicked Save');
}
</script>

<template>
<div class="menu">
    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.right="'Create a new project.'"
                @click="onClickSave">
                <i class="fa-regular fa-save menu-icon"></i>
                <span>
                    New Project
                </span>
            </Button>

            <Button text
                class="menu-button"
                v-tooltip.bottom="'Update project list.'"
                @click="onClickSave">
                <i class="fa-solid fa-rotate menu-icon"></i>
                <span>
                    Update List
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
                v-tooltip.bottom="'Import a new data file.'"
                @click="onClickNewFile">
                <i class="fa-regular fa-file menu-icon"></i>
                <span>
                    Add File
                </span>
            </Button>

            <Button text
                class="menu-button"
                v-tooltip.bottom="'Update project list.'"
                @click="onClickSave">
                <i class="fa-solid fa-rotate menu-icon"></i>
                <span>
                    Update List
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            File
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

<Panel class="h-full project-list">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa-solid fa-list"></i>
                        All Projects
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


<Panel class="h-full project-detail">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa-solid fa-briefcase"></i>
                        Project Detail
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
.project-list {
    width: 400px;
    margin: 0 0.5rem 0 0;
}
.project-detail {
    width: calc(100% - 400px);
}
</style>