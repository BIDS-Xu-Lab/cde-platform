<script setup>
import { viewDepthKey } from "vue-router";
import { useDataStore } from "../DataStore";
import { ref } from "vue";
import { Jimin } from "../Jimin";

defineProps({
    file: Object,
    view_mode: String
});

const store = useDataStore();
const visible_dialog_move_file = ref(false);
const popover_review_results_list = ref(null);
const togglePopoverReviewResultsList = (event) => {
    popover_review_results_list.value.toggle(event);
}
const visible_dialog_loading = ref(false);
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
    visible_dialog_loading.value = true;
    // set working project to this project
    store.working_project = store.current_project;

    // set working file to this file
    store.working_file = file;

    // set working concepts
    try {
        let ret = await Jimin.getConceptAndMappingByFile(file.file_id);
        console.log('* got concepts:', ret);

        // set working concepts and mapping to default
        store.working_file_concepts = ret.concepts;
        store.working_mappings = {};

        // put all concepts into the working mappings
        ret.mappings.forEach((mapping) => {
            store.working_mappings[mapping.concept_id] = {
                selected_results: mapping.selected_results,
                search_results: mapping.search_results,
                reviewed_results: mapping.reviewed_results,
                mapper_suggestion: mapping.mapper_suggestion,
                reviewer_suggestion: mapping.reviewer_suggestion,
                status: mapping.status
            };
        });

    } catch (err) {
        console.error(err);
        store.msg(err.message, 'Error', 'error');
        return;
    }

    // then, switch to the mapping view
    store.changeView('mapping');
    visible_dialog_loading.value = false;
}

async function onClickReview(file, user_id) {
    console.log('* clicked Review button');
    // clear the existing mapping data
    store.clearMappingData();
    visible_dialog_loading.value = true;
    // set working project to this project
    store.working_project = store.current_project;

    // set working file to this file
    store.working_file = file;
    // then, switch to the mapping view
    try{
        let ret = await Jimin.getConceptAndReviewDataByFile(file.file_id, user_id);
        console.log('* got concept:', ret);
                // set working concepts and mapping to default
                store.working_file_concepts = ret.concepts;
                store.working_mappings = {};

                // put all concepts into the working mappings
                ret.mappings.forEach((mapping) => {
                    store.working_mappings[mapping.concept_id] = {
                        selected_results: mapping.selected_results,
                        search_results: mapping.search_results,
                        reviewed_results: mapping.reviewed_results,
                        mapper_suggestion: mapping.mapper_suggestion,
                        reviewer_suggestion: mapping.reviewer_suggestion,
                        status: mapping.status
                    };
                });
    } catch (err) {
        console.error(err);
        store.msg(err.message, 'Error', 'error');
        return;
    }
    visible_dialog_loading.value = false;
    store.changeView('review');
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

async function onClickChangeStage() {
    console.log('* clicked Change Stage');
    visible_dialog_move_file.value = true;
}


async function onClickMoveStage(file, stage) {
    visible_dialog_move_file.value = false;
    console.log('* clicked move stage');
    // delete this file
    let ret = await Jimin.moveToNextStage(file.file_id, stage);
    // if this file is the working file, reset the working file
    if (store.working_file && file.file_id == store.working_file.file_id) {
        store.working_file = null;
        store.working_file_concepts = [];
        store.working_concept = null;
        store.grand_review_data = [];
    }

    store.msg(ret.message);

    // update all files for this project
    await store.updateCurrentProjectFiles();
}

async function onClickgrandReview(file) {
    console.log('* clicked Grand Review');
    let ret = await Jimin.moveToNextStage(file.file_id, "grand_review");
    store.msg(ret.message);
    // update files by related project
    await store.updateCurrentProjectFiles();
    await onClickContinue(store.files.find(f => f.file_id === file.file_id));
}

async function onClickContinue(file) {
    console.log('* clicked Continue Grand Review');
    store.clearMappingData();
    visible_dialog_loading.value = true;
    try {
        let ret = await Jimin.getConceptAndGrandReviewByFile(file.file_id);
        store.working_mappings = {};
        console.log('* got concept:', ret);
        store.working_file_concepts = ret.concepts;
        store.grand_review_data = ret.grand_review_data;
        store.working_file = file;
        store.working_project = store.current_project;
        ret.mappings.forEach((mapping) => {
                    store.working_mappings[mapping.concept_id] = {
                        selected_results: mapping.selected_results,
                        search_results: mapping.search_results,
                        reviewed_results: mapping.reviewed_results,
                        mapper_suggestion: mapping.mapper_suggestion,
                        reviewer_suggestion: mapping.reviewer_suggestion,
                        status: mapping.status
                    };
                });
    } catch (err) {
        console.error(err);
        store.msg(err.message, 'Error', 'error');
        return;
    }
    store.changeView('grand_review');
    visible_dialog_loading.value = false;
}

async function onClickView(file, user_id) {
    console.log('* clicked View button');
    // clear the existing mapping data
    store.clearMappingData();

    // set working project to this project
    store.working_project = store.current_project;

    // set working file to this file
    store.working_file = file;
    // then, switch to the mapping view
    try{
        let ret = await Jimin.getConceptAndReviewDataByFile(file.file_id, user_id);
        console.log('* got concept:', ret);
                // set working concepts and mapping to default
                store.working_file_concepts = ret.concepts;
                store.working_mappings = {};

                // put all concepts into the working mappings
                ret.mappings.forEach((mapping) => {
                    store.working_mappings[mapping.concept_id] = {
                        selected_results: mapping.selected_results,
                        search_results: mapping.search_results,
                        reviewed_results: mapping.reviewed_results,
                        mapper_suggestion: mapping.mapper_suggestion,
                        reviewer_suggestion: mapping.reviewer_suggestion,
                        status: mapping.status
                    };
                });
    } catch (err) {
        console.error(err);
        store.msg(err.message, 'Error', 'error');
        return;
    }
    store.changeView('review');
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
        <div class="text-lg font-bold mb-2">
                <font-awesome-icon :icon="['fa', 'file']" />
                {{ file.filename }}
        </div>
        <div class="file-column flex flex-row mb-2">
            <div class="flex flex-col items-center mr-4"
                v-if="view_mode === 'file' && file.round[file.round.length - 1].stage === 'mapping'">
                <div class="text-sm">Mapped / Mapper</div>
                <p class="text-xl font-bold">
                    {{ file.n_submitted }} / {{ store.current_project.members.filter(member => member.role === 'mapper').length + 1}}
                </p>
            </div>
            <div class="flex flex-col items-center mr-4"
                v-if="view_mode === 'file' && file.round[file.round.length - 1].stage === 'reviewing'">
                <div class="text-sm">Reviewed / Mapped Result</div>
                <p class="text-xl font-bold">
                    {{ file.n_reviewed }} / {{ file.n_submitted * (store.current_project.members.filter(member => member.role === 'reviewer').length + 1)}}
                </p>
            </div>
            <div class="flex flex-col items-center mr-4"
                v-if="view_mode === 'file'">
                    <div class="text-sm">Current Status</div>
                    <div class="flex flex-row">
                        <p class="text-xl font-bold">
                            {{ file.round[file.round.length - 1].stage }}
                        </p>
                    </div>
            </div>
            <div class="flex flex-col mr-4" v-if="file.round[file.round.length - 1].stage === 'reviewing'">
                <div class="text-sm">Review Round</div>
                <p class="text-xl font-bold">
                    {{ file.round.length }}
                </p>
            </div>
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
                @click="togglePopoverReviewResultsList">
                <font-awesome-icon :icon="['fa', 'list']" />
                Results List
            </Button>
            <Popover ref="popover_review_results_list">
                <div class="flex flex-col gap-4 w-[25rem]">
                    <div class="font-bold">
                        <div style="border-bottom: 1px solid var(--bd-color)">
                            <span class="font-bold">Result List:</span>
                        </div>
                        <div class = "flex justify-center" v-if="file.n_submitted === 0">
                            No review results available. 
                        </div>
                        <li v-for="review in file.submitted_users" class="flex items-center gap-2 px-2 py-3 rounded-border">
                            <div class="flex justify-between w-full mt-1 mb-1">
                                <div>
                                    <span class="text-xl font-bold">Name: {{ store.current_project.members.find(member => member.user_id === review)?.name }}</span>
                                    <div class="text-sm text-surface-500 dark:text-surface-400">Email: {{ store.current_project.members.find(member => member.user_id === review)?.email }}</div>
                                </div>
                                <Button
                                    severity="info"
                                    size="small"
                                    class="m-2 btn-mini"
                                    @click="onClickReview(file, review)"
                                    >
                                    <font-awesome-icon :icon="['fa', 'eye']" 
                                    v-tooltip.bottom="'View review results for this file.'"/>
                                    Review
                                </Button>
                            </div>
                        </li>
                    </div>
                </div>
            </Popover>

            <!-- <Button 
                severity="info"
                size="small"
                class="mr-2"
                v-tooltip.bottom="'Download this file.'"
                @click="onClickDownload(file)">
                <font-awesome-icon :icon="['fa', 'download']" />
                Download
            </Button> -->

            <Button 
                severity="danger"
                size="small"
                class="mr-2"
                v-if="view_mode === 'file'"
                :disabled="store.working_file?.file_id == file.file_id"
                v-tooltip.bottom="'Delete this file.'"
                @click="onClickDeleteFile(file)">
                <font-awesome-icon :icon="['fa', 'trash']" />
                Delete
            </Button>
            <Button 
                severity="warn"
                size="small"
                v-if="view_mode === 'file' && file.round[file.round.length - 1].stage !== 'grand_review' && file.round[file.round.length - 1].stage !== 'finalized'"
                :disabled="(file.round[file.round.length - 1].stage === 'mapping' && file.n_submitted === 0) || file.round[file.round.length - 1].stage === 'reviewing' && file.n_reviewed === 0"
                v-tooltip.bottom="'Change the stage.'"
                @click="onClickChangeStage()">
                <font-awesome-icon :icon="['fas', 'arrow-right']" />
                Change the stage
            </Button>
            <Button 
                severity="info"
                size="small"
                v-if="view_mode === 'file' && file.round[file.round.length - 1].stage ==='grand_review'"
                :disabled="file.round[file.round.length - 1].stage === 'completed'"
                v-tooltip.bottom="'Grand Review.'"
                @click="onClickContinue(file)">
                <font-awesome-icon :icon="['fas', 'fa-eye']" />
                Continue Grand Review
            </Button>
            <Button 
                severity="info"
                size="small"
                v-if="view_mode === 'file' && file.round[file.round.length - 1].stage ==='finalized'"
                :disabled="file.round[file.round.length - 1].stage === 'completed'"
                v-tooltip.bottom="'View Result'"
                @click="onClickView(file, store.user.user_id)">
                <font-awesome-icon :icon="['fas', 'fa-eye']" />
                View
            </Button>
        </div>

    </div>
    <Dialog v-model:visible="visible_dialog_move_file" header="Move Stage" width="400px">
        <div v-if="file.round[file.round.length - 1].stage==='mapping'" class="flex flex-col gap-4">
            <p>Please confirm all mappers finished</p>
            <div class="flex flex-row justify-end gap-2">
                <Button 
                severity="secondary" 
                @click="visible_dialog_move_file = false">
                <font-awesome-icon :icon="['fas', 'xmark']" />
                Cancel
                </Button>

                <Button 
                severity="warn" 
                @click="onClickMoveStage(file, 'reviewing')">
                <font-awesome-icon :icon="['fas', 'arrow-right']" />
                Start Review
                </Button>
            </div>
        </div>
        <div v-if="file.round[file.round.length - 1].stage==='reviewing'" class="flex flex-col gap-4">
            <p>Do you want to grand review of this file?</p>
            <div class="flex flex-row justify-end gap-2">
                <Button 
                severity="secondary" 
                @click="visible_dialog_move_file = false">
                <font-awesome-icon :icon="['fas', 'xmark']" />
                Cancel
                </Button>
                <Button 
                severity="info" 
                @click="onClickgrandReview(file)">
                <font-awesome-icon :icon="['fas', 'rotate-right']" />
                Grand Review
                </Button>
                <!-- <Button
                severity="danger"
                @click="onClickMoveStage(file, 'completed')">
                <font-awesome-icon :icon="['fas', 'check']" />
                Finalize
                </Button> -->
            </div>
        </div>
    </Dialog>
    <Dialog v-model:visible="visible_dialog_loading" modal header="Processing" :closable="false" :style="{ width: '300px' }">
        <div class="flex flex-col items-center justify-center p-4">
            <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="8" fill="transparent"
                animationDuration=".5s" aria-label="Custom ProgressSpinner" />
            <p class="mt-3">Please wait while processing...</p>
        </div>
    </Dialog>
</template>

<style scoped>
</style>