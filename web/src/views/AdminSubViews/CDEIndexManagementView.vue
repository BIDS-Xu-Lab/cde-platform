<script setup>
import { useDataStore } from "../../DataStore";
import { ref } from "vue";
import { AWS } from '../../AWS';

const store = useDataStore();

///////////////////////////////////////////////////////////
// Index management
///////////////////////////////////////////////////////////

async function onClickInitializeSampleCDEs() {
    console.log('* clicked Initialize Sample CDEs');

    // confirm 
    if (!confirm(`Are you sure to initialize sample CDEs? This action cannot be undone.`)) {
        return;
    }

    // final confirmation ask yes?
    if (!confirm('Are you really sure?')) {
        return;
    }

    // initialize elasticsearch
    try {
        let data = await AWS.initElasticsearch();
        console.log('data:', data);
        store.msg('Server returns: ' + data.message);

    } catch (error) {
        console.log('error:', error);
        store.msg('Failed to initialize sample CDEs.', 'Error', 'error');
    }
}

async function onClickClearAllCDEs() {
    console.log('* clicked Clear All CDEs');

    // confirm 
    if (!confirm(`Are you sure to clear all CDEs? This action cannot be undone.`)) {
        return;
    }

    // final confirmation ask yes?
    if (!confirm('Are you really sure?')) {
        return;
    }

    // clear all CDEs
    try {
        let data = await AWS.clearElasticsearch();
        console.log('data:', data);
        store.msg('Server returns: ' + data.message);

    } catch (error) {
        console.log('error:', error);
        store.msg('Failed to clear all CDEs.', 'Error', 'error');
    }
}

</script>

<template>
<div class="w-full h-full flex flex-row">
    <Panel class="h-full w-1/4">
        <template #header>
            <div class="w-full flex justify-between">
                <div class="flex">
                    <div class="flex-col">
                        <div class="text-lg font-bold">
                            <i class="fa-solid fa-database"></i>
                            Quick ES Index Management
                        </div>
                        <div class="panel-subtitle text-sm">
                        </div>
                    </div>
                </div>
                <div>

                </div>
            </div>
        </template>


        <div class="flex flex-col justify-start">

            <Button severity="secondary"
                class="mb-2"
                v-tooltip.bottom="'Initialize the database with all collections.'"
                @click="onClickInitializeSampleCDEs(true)">
                <i class="fa-solid fa-sync"></i>
                Initialize Sample CDEs(Development Purpose Only)
            </Button>

            <Button severity="danger"
                class="mb-2"
                v-tooltip.bottom="'Update project list.'"
                @click="onClickClearAllCDEs(true)">
                <i class="fa-solid fa-sync"></i>
                Clear All CDEs (Danger!)
            </Button>
        </div>
    </Panel>
</div>
</template>

<style scoped>
</style>