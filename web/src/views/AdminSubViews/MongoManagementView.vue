<script setup>
import { useDataStore } from "../../DataStore";
import { ref } from "vue";
import { AWS } from '../../AWS';

const store = useDataStore();

///////////////////////////////////////////////////////////
// Mongo management
///////////////////////////////////////////////////////////
async function onClickClearAllCollections(flag_skip_users=true) {
    console.log('* clicked Clear All Collections');

    // confirm 
    if (!confirm(`Are you sure to clear all collections with (flag_skip_users=${flag_skip_users})? This action cannot be undone.`)) {
        return;
    }

    // final confirmation ask yes?
    if (!confirm('Are you really sure?')) {
        return;
    }

    // clear all collections
    try {
        let exclude_collections = flag_skip_users ? ['users'] : [];
        let data = await AWS.clearDatabase(exclude_collections);
        console.log('data:', data);

        store.msg('Server returns: ' + data.message);
    } catch (error) {
        console.log('error:', error);
        store.msg('Failed to clear all collections.', 'Error', 'error');
    }
}

async function onClickInitializeAllCollections(flag_skip_users=true) {
    console.log('* clicked Initialize All Collections');

    // final confirmation ask yes?
    if (!confirm('Are you really sure?')) {
        return;
    }

    // initialize all collections
    try {
        let data = await AWS.initDatabase();
        console.log('data:', data);
        store.msg('Server returns: ' + data.message);

    } catch (error) {
        console.log('error:', error);
        store.msg('Failed to initialize all collections.', 'Error', 'error');
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
                            <i class="fa-solid fa-diagram-project"></i>
                            Quick Database Management
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
                @click="onClickInitializeAllCollections(true)">
                <i class="fa-solid fa-sync"></i>
                Initialize All Collections (Except users)
            </Button>

            <Button severity="danger"
                class="mb-2"
                v-tooltip.bottom="'Update project list.'"
                @click="onClickClearAllCollections(true)">
                <i class="fa-solid fa-sync"></i>
                Clear All Collections (Except users)
            </Button>
        </div>
    </Panel>
</div>
</template>

<style scoped>
</style>