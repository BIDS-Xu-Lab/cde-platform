<script setup>
import { onMounted } from 'vue';
import { useDataStore } from '../DataStore';
const store = useDataStore();

async function onClickRefreshList() {
    console.log('* clicked Refresh list');

    // ask server for updated statistics
    let data = await Jimin.getStats();

    store.msg('Updated statistics.');

    // set stats to store
    store.stats = data.stats;
}

onMounted(() => {
    console.log('* mounted DashboardView');

    // update stats only if store stats is null
    if (store.stats == null) {
        onClickRefreshList();
    }
});
</script>

<template>
<div class="menu">
    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                @click="onClickRefreshList">
                <i class="fa-solid fa-rotate menu-icon"></i>
                <span>
                    Refresh
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Data
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


<div class="main flex-row">

<Panel v-if="store.stats"
    class="mr-2"
    style="width: 500px;">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa-solid fa-briefcase"></i>
                        My Statistics
                    </div>
                    <div class="panel-subtitle text-sm">
                    </div>
                </div>
            </div>
            <div>

            </div>
        </div>
    </template>

    <div class="flex flex-row justify-between items-baseline">
        <div class="flex flex-col justify-center items-center mb-10">
            <span class="text-4xl font-bold">
                {{ store.stats.n_projects }}
            </span>
            <span class="text-lg">
                Projects
            </span>
        </div>

        <div class="flex flex-col justify-center items-center mb-10">
            <span class="text-4xl font-bold">
                {{ store.stats.n_files }}
            </span>
            <span class="text-lg">
                Files
            </span>
        </div>

        <div class="flex flex-col justify-center items-center mb-10">
            <span class="text-4xl font-bold">
                {{ store.stats.n_concepts }}
            </span>
            <span class="text-lg">
                Concepts
            </span>
        </div>

        <div class="flex flex-col justify-center items-center mb-4">
            <span class="text-4xl font-bold">
                {{ store.stats.n_mappings }}
            </span>
            <span class="text-lg">
                Mappings
            </span>
        </div>
        
    </div>
</Panel>


</div>

</template>

<style scoped>
</style>