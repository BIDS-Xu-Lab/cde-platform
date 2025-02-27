<script setup>
import { useDataStore } from "../DataStore";
import { ref } from "vue";
const store = useDataStore();

const props = defineProps({
    item: Object,
    item_idx: Number,
    flag_selected: Boolean || false,
    flag_enabled_value_mapping: Boolean || false,
    flag_submitted: Boolean || false,
    view_mode: String,
});

const popover_disagree_comments = ref(null);

const togglePpoverDisagreeComments = (event) => {
    // set comments to the original comment
    comments.value = store.working_mappings[store.working_concept.concept_id].reviewed_results[props.item_idx]?.comment;
    popover_disagree_comments.value.toggle(event);
}

const popover_view_comments = ref(null);

const togglePpoverviewComments = (event) => {
    // if show_edit_comments is true, set it to false
    if (show_edit_comments.value) {
        show_edit_comments.value = false;
    }
    popover_view_comments.value.toggle(event);
}

const agree_comment_dialog_visible = ref(false);

const agreeOptions = [
    { label: 'With Comments', icon: 'pi pi-check', command: () => { 
        // set comments to the original comment
        comments.value = store.working_mappings[store.working_concept.concept_id].reviewed_results[props.item_idx]?.comment;
        agree_comment_dialog_visible.value = true; 
    } }
];

const show_edit_comments = ref(false);
function toggleShowEditComments() {
    // set comments to the original comment
    comments.value = store.working_mappings[store.working_concept.concept_id].reviewed_results[props.item_idx]?.comment;
    show_edit_comments.value = !show_edit_comments.value;
}

async function onClickEditSubmit() {
    console.log('* clicked Edit Submit:', comments.value);
    // Maintain the original agreement status when editing comments
    const currentAgreement = store.working_mappings[store.working_concept.concept_id].reviewed_results[props.item_idx]?.agreement;
    console.log('* currentAgreement:', currentAgreement); 
    // update store
    store.working_mappings[store.working_concept.concept_id].reviewed_results[props.item_idx].comment = comments.value;
    // send selected results to server
    let ret = await Jimin.updateSelectedResults(
        store.working_concept.concept_id,
        store.working_file.round.length - 1,
        store.working_mappings[store.working_concept.concept_id].selected_results,
        store.working_mappings[store.working_concept.concept_id].reviewed_results
    );
    console.log('* updated selected results:', ret);
    // clear the comments
    comments.value = '';
    // show a message
    store.msg(ret.message);
    toggleShowEditComments();
    togglePpoverviewComments();
}

const comments = ref(store.working_mappings[store.working_concept.concept_id].reviewed_results[props.item_idx]?.comment || '');

async function onClickSelectResult(result) {
    console.log('* clicked Select Result:', result);

    // update store
    store.addSelectedResultToWorkingConcept(result);

    // send selected results to server
    let ret = await Jimin.updateSelectedResults(
        store.working_concept.concept_id,
        store.working_file.round.length - 1,
        store.working_mappings[store.working_concept.concept_id].selected_results
    );

    console.log('* updated selected results:', ret);

    // show a message
    store.msg(ret.message);
}

async function onClickRemoveResult(result) {
    console.log('* clicked Remove Result:', result);

    // update store
    store.removeSelectedResultFromWorkingConcept(result);

    // send selected results to server
    let ret = await Jimin.updateSelectedResults(
        store.working_concept.concept_id,
        store.working_file.round.length - 1,
        store.working_mappings[store.working_concept.concept_id].selected_results
    );

    console.log('* updated selected results:', ret);

    // show a message
    store.msg(ret.message);
}

function fmtScore(score) {
    return score.toFixed(2);
}


function itemValueCheck(item) {
    if (item.values?.length > 0) {
        return true;
    } else {
        return false;
    }
}

async function onChangeValueMapping(item, value) {
    console.log('* changed Value Mapping:', item, value);

    // send selected results to server
    let ret = await Jimin.updateSelectedResults(
        store.working_concept.concept_id,
        store.working_file.round.length - 1,
        store.working_mappings[store.working_concept.concept_id].selected_results
    );

    console.log('* updated value mapping:', ret);

    // show a message
    store.msg(ret.message);
}

async function onClickDeselectValueMapping(item, value) {
    console.log('* clicked Deselect Value Mapping:', item, value);
    item.value_mapping[value] = '';

    // send selected results to server
    let ret = await Jimin.updateSelectedResults(
        store.working_concept.concept_id,
        store.working_file.round.length - 1,
        store.working_mappings[store.working_concept.concept_id].selected_results
    );

    console.log('* updated value mapping:', ret);

    // show a message
    store.msg(ret.message);
}

function checkRemoveButtonAuth() {
    // check the props.item_idx, if item_idx larger than store.working_mappings[store.working_concept.concept_id].reviewed_results.length - 1, then return true
    if (props.flag_selected && !props.flag_submitted) {
        if (props.view_mode === 'reviewing' && props.item_idx < store.working_mappings[store.working_concept.concept_id].reviewed_results.length) {
            return false;
        } else {
            return true;
        }
    } else {
        return false;
    }
}

async function onClickAgree(item_idx){
    console.log('* clicked Agree:', props.item, item_idx);
    // update store
    store.working_mappings[store.working_concept.concept_id].reviewed_results[item_idx].agreement = true;
    store.working_mappings[store.working_concept.concept_id].reviewed_results[item_idx].comment = "No comment.";
    // send selected results to server
    let ret = await Jimin.updateSelectedResults(
        store.working_concept.concept_id,
        store.working_file.round.length - 1,
        store.working_mappings[store.working_concept.concept_id].selected_results,
        store.working_mappings[store.working_concept.concept_id].reviewed_results
    );

    console.log('* updated selected results:', ret);
    // show a message
    store.msg(ret.message);
}

async function onClickAgreementSubmit(item_idx, agree, comment) {
    console.log('* clicked disagree:', props.item, item_idx);
    // update store
    // close the popover
    if(agree === false){
        togglePpoverDisagreeComments();
    }
    if(agree === true){
        agree_comment_dialog_visible.value = false;
    }
    // check if the comment is empty
    if (comment === ''){
        comment = "No comment.";
    }
    // update store
    store.working_mappings[store.working_concept.concept_id].reviewed_results[item_idx].agreement = agree;
    store.working_mappings[store.working_concept.concept_id].reviewed_results[item_idx].comment = comment;
    // clear the comment
    comments.value = '';
    // send selected results to server
    let ret = await Jimin.updateSelectedResults(
        store.working_concept.concept_id,
        store.working_file.round.length - 1,
        store.working_mappings[store.working_concept.concept_id].selected_results,
        store.working_mappings[store.working_concept.concept_id].reviewed_results
    );

    console.log('* updated selected results:', ret);
    // show a message
    store.msg(ret.message);

}
function displayAgreementInfo(){
    if (store.working_mappings[store.working_concept.concept_id].reviewed_results[props.item_idx]?.agreement === true){
        return "Agreed";
    } else if (store.working_mappings[store.working_concept.concept_id].reviewed_results[props.item_idx]?.agreement === false){
        return "Disagreed";
    } 
    else if (store.working_mappings[store.working_concept.concept_id].reviewed_results.length < props.item_idx + 1){
        return "Reviewer selected";
    } else {
        return "Not reviewed";
    }
}

function selectionDisabled() {
    if (props.view_mode === 'mapping'){
        return store.working_mappings[store.working_concept.concept_id]?.mapper_suggestion;
    } else if (props.view_mode === 'reviewing'){
        return store.working_mappings[store.working_concept.concept_id]?.reviewer_suggestion;
    } else {
        return false;
    }
}
</script>

<template>
<div class="result-line"
    :class="{ 'disabled-term': store.working_concept.final && view_mode === 'reviewing' }">
    <div class="result-tags">
        <div class="flex flex-row">
            <Badge :value="fmtScore(item.score)" 
                class="mr-1 badge-score"
                severity="info" />
            <Badge :value="item.term_source" severity="info" />
        </div>

        <div>

        </div>
    </div>
    <div class="result-name">
        <div class="flex items-center">
            <div class="font-bold text-lg">
                {{ item.term }}
            </div>
            <Divider layout="vertical" class="!mx-2" />
            <div class="text-base">
                <a :href="'https://cde.nlm.nih.gov/deView?tinyId=' + item.term_id"
                    title="Open this CDE in NIH CDE Browser in a new tab."
                    target="_blank">
                    <font-awesome-icon :icon="['fa', 'globe']" />
                    {{ item.term_id }}
                </a>
            </div>
        </div>

        <div>
        </div>  
    </div>

    <div class="result-detail">
        <span class="font-bold">
            Question Text:
        </span>
        {{ item.description }}
    </div>

    <div class="result-values">
        <span class="font-bold">
            Values:
        </span>
        <span v-if="item.values?.length > 0">
            {{ item.values }}
        </span>
        <span v-else class="text-sm">
            <font-awesome-icon :icon="['fa', 'info-circle']" />
            No values available.
        </span>
    </div>

    <div class="flex flex-row mt-2 mb-1 items-baseline justify-between">
        <div>
            <div v-if="flag_enabled_value_mapping && itemValueCheck(item)"
                class="font-bold mb-4 ml-2">
                <font-awesome-icon :icon="['fa', 'list']" />
                Value Mapping
            </div>


            <!-- <Button
                v-if="flag_enabled_value_mapping && itemValueCheck(item)"
                size="small"
                icon="pi pi-list"
                label="Save Value Mapping"
                severity="success"
                class=""
                v-tooltip.right="'Map values for this CDE.'"
                @click="onClickSaveMapping(item)">
            </Button> -->
        </div>

        <div>
            <Button v-if="!flag_selected && !flag_submitted"
                :disabled="selectionDisabled()"
                size="small"
                icon="pi pi-check"
                severity="success"
                label="Select"
                class="mr-2"
                v-tooltip.right="'Select this concept.'"
                @click="onClickSelectResult(item)">
            </Button>
            <Button v-if="checkRemoveButtonAuth()"
                size="small"
                severity="warn"
                icon="pi pi-trash"
                label="Remove"
                class="mr-2"
                v-tooltip.right="'Remove this concept.'"
                @click="onClickRemoveResult(item)">
            </Button>
            <div class = "flex flex-row" v-if="view_mode === 'reviewing' && flag_selected && !checkRemoveButtonAuth()">
                <div class="flex flex-row">
                    <p class="font-bold mr-2">{{ displayAgreementInfo()}}</p>
                    <div class="font-bold">
                        <Button
                        :disabled="store.working_mappings[store.working_concept.concept_id].reviewed_results[item_idx] === undefined"
                    size="small"
                    severity="info"
                    icon="pi pi-eye"
                    label="Comments"
                    class="mr-2"
                    v-tooltip.right="'View comments'"
                    @click="togglePpoverviewComments">
                </Button>
                <Popover ref="popover_view_comments">
                    <div class="flex flex-col gap-4 w-[25rem]">
                        <div class="font-bold">
                            <div style="border-bottom: 1px solid var(--bd-color)">
                                <span class="font-bold">Comments</span>
                            </div>
                            <div class="flex flex-col items-center">
                                <div v-if="!show_edit_comments">
                                    <p v-if="store.working_mappings[store.working_concept.concept_id].reviewed_results[item_idx].comment" class="mt-4 mb-2 w-[24rem]">{{store.working_mappings[store.working_concept.concept_id].reviewed_results[item_idx].comment}}</p>
                                    <p v-else class="mt-4 mb-2 w-[24rem]">No comments available</p>
                                </div>
                                <div v-if="show_edit_comments" class="w-full mb-4">
                                    <Textarea
                                        v-model="comments"
                                        rows="5"
                                        class="w-full"
                                        placeholder="Enter your comments here..."
                                    />
                                </div>
                                <div class="flex flex-row">
                                    <Button
                                        v-if="!show_edit_comments"
                                        severity="primary"
                                        size="small"
                                        class="btn-mini w-24 mr-2"
                                        @click="toggleShowEditComments"
                                        >
                                        Edit
                                    </Button>
                                    <Button 
                                        v-if="show_edit_comments"
                                        severity="secondary"
                                        size="small"
                                        class="btn-mini w-24 ml-2"
                                        @click="onClickEditSubmit()"
                                        >
                                        Submit
                                    </Button>
                                    <Button 
                                        severity="secondary"
                                        size="small"
                                        class="btn-mini w-24 ml-2"
                                        @click="togglePpoverviewComments"
                                        >
                                        Close
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </div>
                </Popover>
                    </div>
                </div>
                <SplitButton
                    v-if="!flag_submitted"
                    :disabled="store.working_mappings[store.working_concept.concept_id].reviewed_results[item_idx].agreement === true || store.working_mappings[store.working_concept.concept_id].reviewer_suggestion"
                    size="small"
                    severity="success"
                    icon="pi pi-check"
                    label="Agree"
                    class="mr-2"
                    v-tooltip.right="'Aggree this selection'"
                    @click="onClickAgreementSubmit(item_idx, true, comments)"
                    :model="agreeOptions"
                    >
                </SplitButton>
                <Button
                    v-if="!flag_submitted"
                    :disabled="store.working_mappings[store.working_concept.concept_id].reviewed_results[item_idx].agreement === false"
                    size="small"
                    severity="danger"
                    icon="pi pi-times"
                    label="Disagree"
                    class="mr-2"
                    v-tooltip.right="'Disagree this selection'"
                    @click="togglePpoverDisagreeComments">
                </Button>
                <Popover ref="popover_disagree_comments">
                    <div class="flex flex-col gap-4 w-[25rem]">
                        <div class="font-bold">
                            <div style="border-bottom: 1px solid var(--bd-color)">
                                <span class="font-bold">Comments</span>
                            </div>
                            <div class="flex flex-col items-center">
                                <Textarea class="mt-4 mb-2 w-[24rem]" v-model="comments" rows="5" cols="30" placeholder="Input comments here, or press submit without comments." />
                                <Button
                                    severity="secondary"
                                    size="small"
                                    class="btn-mini w-24"
                                    @click="onClickAgreementSubmit(item_idx, false, comments)"
                                    >
                                    Submit
                                </Button>
                            </div>
                        </div>
                    </div>
                </Popover>
            </div>
        </div>
    </div>

    <div v-if="flag_enabled_value_mapping && itemValueCheck(item)" 
        class="flex flex-col value-mapping">
        <div v-for="value in store.working_concept.values"
            class="value-mapping-item flex flex-row items-center mb-2">
            <div class="h-full ml-4">
                <Tag class="w-96" :value="value" />
            </div>
            <div class="mx-4">
                <template v-if="item.value_mapping[value]">
                    <font-awesome-icon :icon="['fa', 'arrow-right']" />
                </template>
                <template v-else>
                    <font-awesome-icon :icon="['fa', 'times']" />
                </template>
            </div>

            <Select v-model="item.value_mapping[value]"
                :disabled="flag_submitted || view_mode === 'reviewing'"
                @change="onChangeValueMapping(item, value)"
                filter 
                :options="item.values"
                placeholder="Select a value"
                style="width: 20rem;"
                v-tooltip.right="'Select a value to map.'" />

            <Button v-if="item.value_mapping[value] && !flag_submitted && view_mode != 'reviewing'"
                severity="danger"
                size="small"
                icon="pi pi-trash"
                label="Deselect"
                class="ml-2"
                v-tooltip.right="'Deselect the current value mapping.'"
                @click="onClickDeselectValueMapping(item, value)" />
        </div>
    </div>
</div>
<Dialog v-model:visible="agree_comment_dialog_visible" 
    modal 
    header="Comments" 
    :style="{ width: '400px' }" 
    :closable="true">
    <div class="flex flex-col gap-4 w-[25rem]">
        <div class="font-bold">
            <div class="flex flex-col items-center">
                <Textarea class="mt-4 mb-2 w-[24rem]" v-model="comments" rows="5" cols="30" placeholder="Input comments here, or press submit without comments." />
                <Button
                    severity="secondary"
                    size="small"
                    class="btn-mini w-24"
                    @click="onClickAgreementSubmit(item_idx, true, comments)"
                    >
                    Submit
                </Button>
            </div>
        </div>
    </div>
</Dialog>
</template>

<style scoped>
.result-line {
    width: 100%;
    border-bottom: 1px solid var(--bd-color);
    padding: 0.5rem 0;
    display: flex;
    flex-direction: column;
}
.result-line:last-child {
    border-bottom: 0;
}
.result-tags {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
}
.result-name {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    font-size: 1.2rem;
}
.badge-score {
    background-color: #857100;
}
.disabled-term {
    pointer-events: none;
    opacity: 0.6; 
}
</style>