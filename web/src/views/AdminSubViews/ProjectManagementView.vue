<script setup>
import { useDataStore } from "../../DataStore";
import { AWS } from '../../AWS';
import { ref } from "vue";

const store = useDataStore();

///////////////////////////////////////////////////////////
// Project management
///////////////////////////////////////////////////////////

// fetch all projects
function onClickRefresProjectList() {
    console.log('* clicked Refresh Project List');
}
</script>

<template>
<div class="h-full w-full flex flex-row">
    
    <Panel class="w-full">
        <template #header>
            <div class="w-full flex justify-start">
                <div class="flex mr-2">
                    <div class="flex-col">
                        <div class="text-lg font-bold">
                            <i class="fa-solid fa-cubes-stacked"></i>
                            All Projects
                        </div>
                        <div class="panel-subtitle text-sm">
                        </div>
                    </div>
                </div>
                <div>
                    <Button 
                        size="small"
                        class="btn-mini"
                        v-tooltip.bottom="'Update project list.'"
                        @click="onClickRefresProjectList">
                        <i class="fa-solid fa-sync"></i>
                        Refresh List
                    </Button>
                </div>
            </div>
        </template>

        <div>
            <DataTable :value="store.admin.projects" 
                paginator 
                :rows="10" 
                :rowsPerPageOptions="[10, 20, 50]" 
                tableStyle="min-width: 50rem">
                <template #empty> No projects found. </template>
                <Column field="name" header="Name" style="width: 40%"></Column>
                <Column field="user" header="Creator / Email" style="width: 30%"></Column>
                <Column header="Actions" style="width: 20%">
                    <template #body="slotProps">
                        <Button icon="pi pi-key" class="p-button-rounded p-button-secondary mr-2"></Button>
                        <Button icon="pi pi-pencil" class="p-button-rounded p-button-success mr-2"></Button>
                        <Button icon="pi pi-trash" class="p-button-rounded p-button-danger"></Button>
                    </template>
                </Column>
            </DataTable>

        </div>
    </Panel>


</div>
</template>

<style scoped>
</style>