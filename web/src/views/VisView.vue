<script setup>
import { useDataStore } from '../DataStore';
const store = useDataStore();

function onClickVis() {
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
                @click="onClickVis">
                <i class="fa-solid fa-pencil menu-icon"></i>
                <span>
                    Visualize CDEs
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Visualization
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

<Panel class="h-full w-full">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa-solid fa-diagram-project"></i>
                        CDE Semantic Map
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
</style>