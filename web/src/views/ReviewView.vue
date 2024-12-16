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
                    Load All Mappings
                </span>
            </Button>

            <Button text
                class="menu-button"
                v-tooltip.right="'Create a new project.'"
                @click="onClickSave">
                <i class="fa-solid fa-calculator menu-icon"></i>
                <span>
                    Evaluate Agreement 
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Mappings
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
<Panel class="h-full term-list">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa fa-list "></i>
                        File List
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

<Panel class="h-full mapping-list">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa fa-list "></i>
                        Mapping List
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

<Panel class="h-full reviewer-panel">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa fa-list "></i>
                        Reviewer
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
.term-list {
    width: 460px;
    min-width: 460px;
    margin: 0 0.5rem 0 0;
}
.mapping-list {
    min-width: 500px;
    margin: 0 0.5rem 0 0;
}
.reviewer-panel {
    min-width: 500px;
    margin: 0 0.5rem 0 0;
}
</style>