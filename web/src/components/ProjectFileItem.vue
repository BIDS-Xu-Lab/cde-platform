<script setup>
import { useDataStore } from "../DataStore";
import { ref } from "vue";

defineProps({
    file: Object
});

const store = useDataStore();
const popover_assign_users = ref(null);

const togglePopoverAssignUsers = (event) => {
    popover_assign_users.value.toggle(event);
}

async function onClickAssignUsers(file) {
    console.log('* clicked Assign Reviewers', file);
    store.msg('Assign reviewers for this file.');
}

async function onClickMapping(file) {
    console.log('* clicked Mapping');

    // clear the existing mapping data
    store.clearMappingData();

    // set working project to this project
    store.working_project = store.current_project;

    // set working file to this file
    store.working_file = file;

    // set working concepts
    try {
        let ret = await Jimin.getConceptsByFile(file.file_id);
        console.log('* got concepts:', ret);

        // set working concepts and mapping to default
        store.working_file_concepts = ret.concepts;
        store.working_mappings = {};

        // put all concepts into the working mappings
        ret.mappings.forEach((mapping) => {
            store.working_mappings[mapping.concept_id] = {
                selected_results: mapping.selected_results,
                search_results: mapping.search_results
            };
        });

    } catch (err) {
        console.error(err);
        store.msg(err.message, 'Error', 'error');
        return;
    }

    // then, switch to the mapping view
    store.changeView('mapping');
}

async function onClickDownload(file) {
    console.log('* clicked Download');
}

// async function onClickMove() {
//     console.log('* clicked Move');
//     visible_dialog_move_file.value = true;
//     await Jimin.moveFile(selected_file_for_move.file_id, selected_project_for_move.project_id);
//     store.msg('Moved file to ' + project.name);
//     selected_file_for_move = null;
//     selected_project_for_move = null;
//     onClickProjectItem(project);
    
    
//     // move this file to selected project
// }
async function onClickDeleteFile(file) {
    console.log('* clicked Delete File');

    // ask for confirmation
    if (!confirm('Are you sure to delete this file?')) {
        return;
    }
    // delete this file
    let ret = await Jimin.deleteFile(file.file_id);
    // if this file is the working file, reset the working file
    if (store.working_file && file.file_id == store.working_file.file_id) {
        store.working_file = null;
        store.working_file_concepts = [];
        store.working_concept = null;
    }

    store.msg(ret.message);

    // update all files for this project
    await store.updateCurrentProjectFiles();
}

</script>

<template>
    <div class="w-full file-item flex flex-col py-2">
        <div class="file-name flex flex-row justify-between">
            <div class="text-lg font-bold">
                <i class="fa fa-file"></i>
                {{ file.filename }}
            </div>
            <div class="file-reviewers">
                Assigned Reviewers: 
                <i class="fa fa-user"></i>

                <Button severity="info"
                    size="small"
                    class="ml-2 btn-mini"
                    @click="togglePopoverAssignUsers"
                    v-tooltip.bottom="'Assign reviewers for this file.'">
                    <i class="fa-solid fa-user-plus"></i>
                    Assign members
                </Button>

                <Popover ref="popover_assign_users">
                    <div class="flex flex-col gap-4 w-[25rem]">
                        <div class="font-bold">
                            Members
                        </div>
                    </div>
                </Popover>
            </div>
        </div>

        <div class="file-column flex flex-row mb-2">
            <div class="flex flex-col mr-4">
                <div class="text-sm"># Columns</div>
                <p class="text-xl font-bold">
                    {{ file.columns.length }}
                </p>
            </div>
            <div class="flex flex-col mr-4">
                <div class="text-sm"># Concepts</div>
                <p class="text-xl font-bold">
                    {{ file.n_concepts }}
                </p>
            </div>
            <div class="flex flex-col mr-4">
                <div class="text-sm">Term Column</div>
                <p class="text-xl font-bold">
                    {{ file.column_name_term }}
                </p>
            </div>

            <div class="flex flex-col mr-4">
                <div class="text-sm">Description Column</div>
                <p class="text-xl font-bold">
                    {{ file.column_name_description }}
                </p>
            </div>

            <div class="flex flex-col mr-4">
                <div class="text-sm">Values Column</div>
                <p class="text-xl font-bold">
                    {{ file.column_name_values }}
                </p>
            </div>
        </div>

        <div class="file-name flex flex-row justify-start">
            <Button 
                severity="secondary"
                size="small"
                class="mr-2"
                v-tooltip.bottom="'Mapping concepts for this file.'"
                @click="onClickMapping(file)">
                <i class="fa-solid fa-magnifying-glass"></i>
                Mapping
            </Button>

            <Button 
                severity="info"
                size="small"
                class="mr-2"
                v-tooltip.bottom="'Download this file.'"
                @click="onClickDownload(file)">
                <i class="fa-solid fa-download"></i>
                Download
            </Button>

            <!-- <Button 
                severity="help"
                size="small"
                class="mr-2"
                v-tooltip.bottom="'Move this file.'"
                @click="visible_dialog_move_file = true; selected_file_for_move = file">
                <i class="fa-solid fa-angles-right"></i>
                move
            </Button> -->

            <Button 
                severity="danger"
                size="small"
                :disabled="store.working_file?.file_id == file.file_id"
                v-tooltip.bottom="'Delete this file.'"
                @click="onClickDeleteFile(file)">
                <i class="fa-solid fa-trash"></i>
                Delete
            </Button>
        </div>

    </div>
</template>

<style scoped>
</style>