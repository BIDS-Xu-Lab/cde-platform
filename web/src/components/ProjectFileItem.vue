<script setup>
import { viewDepthKey } from "vue-router";
import { useDataStore } from "../DataStore";
import { ref } from "vue";

defineProps({
    file: Object,
    view_mode: String
});

const store = useDataStore();
// const popover_assign_users = ref(null);
// const popover_assigned_users = ref(null);

// const togglePopoverAssignUsers = (event) => {
//     popover_assign_users.value.toggle(event);
// }


// const togglePopoverAssignedUsers = (event) =>  {
//     console.log('* clicked View Assigned Member');
//     popover_assigned_users.value.toggle(event);
// }

// async function onClickAssignMember(member, file) {
//     console.log('* clicked Assign Reviewers', member, file);
//     // assign this member to this file
//     let ret = await Jimin.assignMapperToFile(file.file_id, member.user_id);
//     store.msg(ret.message);
//     //  close the popover
//     togglePopoverAssignUsers();
//     // update all files for this project
//     await store.updateCurrentProjectFiles();
//     store.msg('Assign reviewers for this file.');
// }

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
                search_results: mapping.search_results,
                submitted: mapping.submitted
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

async function onClickReview(file){
    console.log('* clicked Review');
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
        
        <!-- <div class="file-name flex flex-row justify-between">
            <div class="text-lg font-bold">
                <font-awesome-icon :icon="['fa', 'file']" />
                {{ file.filename }}
            </div>
            <div class="file-reviewers flex flex-row items-center">
                Assigned Reviewers: 
                <Button severity="secondary"
                    class="mr-1 ml-2" 
                    @click="togglePopoverAssignedUsers" 
                    v-tooltip.bottom="'Click for detail'" 
                    size="small">
                    <font-awesome-icon :icon="['fa', 'user']"/>
                </Button>
                <Popover ref="popover_assigned_users">
                    <div class="flex flex-col gap-4 w-[25rem]">
                            <div class="font-bold">
                                <div class = "flex justify-center" v-if="Object.values(file.file_permission).filter(permission => permission !== 0).length === 0">
                                    No members available.
                                </div>
                                <li v-for="member in store.current_project?.members.filter(member => (member.user_id in file.file_permission && file.file_permission[member.user_id] !== 0))" class="flex items-center gap-2 px-2 py-3 rounded-border">
                                    <div class="flex justify-between w-full">
                                        <div>
                                            <span class="font-medium">{{ member.name }}</span>
                                            <div class="text-sm text-surface-500 dark:text-surface-400">{{ member.email }}</div>
                                        </div>
                                        <Button
                                            severity="danger"
                                            size="small"
                                            class="m-2 btn-mini">
                                            <font-awesome-icon :icon="['fa', 'x']" 
                                            v-tooltip.bottom="'Delete reviewers for this file.'"/>
                                        </Button>
                                    </div>
                                </li>
                            </div>
                        </div>
                </Popover>
                {{ Object.keys(file.file_permission).filter(key => file.file_permission[key] > 0).length }}
                <div v-if="file.file_permission[store.user.user_id] == 0">
                    <Button severity="info"
                        size="small"
                        class="ml-2 btn-mini"
                        @click="togglePopoverAssignUsers"
                        v-tooltip.bottom="'Assign reviewers for this file.'">
                        <font-awesome-icon :icon="['fa', 'user-plus']" />
                        Assign members
                    </Button>
                    <Popover ref="popover_assign_users">
                        <div class="flex flex-col gap-4 w-[25rem]">
                            <div class="font-bold">
                                <div class = "flex justify-center" v-if="store.current_project.members.filter(member => !(member.user_id in file.file_permission)).length === 0">
                                    No members available.
                                </div>
                                <li v-for="member in store.current_project?.members.filter(member => !(member.user_id in file.file_permission))" :key="member.name" class="flex items-center gap-2 px-2 py-3">
                                    <div class="flex justify-between w-full">
                                        <div>
                                            <span class="font-medium">{{ member.name }}</span>
                                            <div class="text-sm text-surface-500 dark:text-surface-400">{{ member.email }}</div>
                                        </div>
                                        <Button severity="success"
                                            class="m-2 btn-mini"
                                            @click="onClickAssignMember(member, file)" 
                                            v-tooltip.bottom="'Click to add this member to the file'" 
                                            size="small">
                                            <font-awesome-icon :icon="['fa', 'plus']"/>
                                        </Button>
                                    </div>
                                </li>
                            </div>
                        </div>
                    </Popover>
                </div>
            </div>
        </div> -->

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
            <div class="flex flex-col mr-4">
                <div class="text-sm">Round</div>
                <p class="text-xl font-bold">
                    {{ file.round.length }}
                </p>
            </div>
        </div>

        <div class="file-name flex flex-row justify-start">
            <Button 
                v-if="view_mode === 'mapping'"
                severity="secondary"
                size="small"
                class="mr-2"
                v-tooltip.bottom="'Mapping concepts for this file.'"
                @click="onClickMapping(file)">
                <font-awesome-icon :icon="['fa', 'magnifying-glass']" />
                Mapping
            </Button>

            <Button 
                v-if="view_mode === 'review'"
                severity="secondary"
                size="small"
                class="mr-2"
                v-tooltip.bottom="'Review result for this file.'"
                @click="onClickReview(file)">
                <font-awesome-icon :icon="['fa', 'magnifying-glass']" />
                Review
            </Button>

            <Button 
                severity="info"
                size="small"
                class="mr-2"
                v-tooltip.bottom="'Download this file.'"
                @click="onClickDownload(file)">
                <font-awesome-icon :icon="['fa', 'download']" />
                Download
            </Button>

            <Button 
                severity="danger"
                size="small"
                :disabled="store.working_file?.file_id == file.file_id"
                v-tooltip.bottom="'Delete this file.'"
                @click="onClickDeleteFile(file)">
                <font-awesome-icon :icon="['fa', 'trash']" />
                Delete
            </Button>
        </div>

    </div>
</template>

<style scoped>
</style>