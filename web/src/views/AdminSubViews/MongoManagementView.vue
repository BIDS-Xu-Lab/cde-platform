<script setup>
import { useDataStore } from "../../DataStore";
import { ref } from "vue";
import { AWS } from '../../AWS';

const store = useDataStore();

///////////////////////////////////////////////////////////
// Mongo management
///////////////////////////////////////////////////////////

</script>

<template>
<div class="w-full h-full flex flex-row">
    <Panel class="h-full w-full">
        <template #header>
            <div class="w-full flex justify-between">
                <div class="flex">
                    <div class="flex-col">
                        <div class="text-lg font-bold">
                            <i class="fa-solid fa-diagram-project"></i>
                            MongoDB Management
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