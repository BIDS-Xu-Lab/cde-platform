<script setup>
import { useDataStore } from "../DataStore";
import { ref } from "vue";
const store = useDataStore();

defineProps({
    item: Object,
    item_idx: Number,
    flag_selected: Boolean || false,
    flag_enabled_value_mapping: Boolean || false,
});

async function onClickSelectResult(result) {
    console.log('* clicked Select Result:', result);

    // update store
    store.addSelectedResultToWorkingConcept(result);

    // send selected results to server
    let ret = await Jimin.updateSelectedResults(
        store.working_concept.concept_id,
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
        store.working_mappings[store.working_concept.concept_id].selected_results
    );

    console.log('* updated selected results:', ret);

    // show a message
    store.msg(ret.message);
}

function fmtScore(score) {
    return score.toFixed(2);
}

function onClickShowValues(item) {
    console.log('* clicked Show Values:', item.values);
    
    // the item.values is a list of values concatenated by a pipe
    // we need to split it into a list of string
    // and we need to remove the white spaces for each value
    let values = item.values.split('|').map(v => v.trim());
    console.log('* values:', values);
}

function itemValueCheck(item) {
    if (item.values?.length > 0) {
        return true;
    } else {
        return false;
    }
}

async function onClickSaveMapping(item) {
    console.log('* clicked Value Mapping:', item);
    
   
}

async function onChangeValueMapping(item, value) {
    console.log('* changed Value Mapping:', item, value);

    // send selected results to server
    let ret = await Jimin.updateSelectedResults(
        store.working_concept.concept_id,
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
        store.working_mappings[store.working_concept.concept_id].selected_results
    );

    console.log('* updated value mapping:', ret);

    // show a message
    store.msg(ret.message);

}

</script>

<template>
<div class="result-line">
    <div class="result-tags">
        <div class="flex flex-row">
            <div class="pr-3">
                {{ item_idx + 1 }}
            </div>
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
                    target="_blank">
                    <i class="fa fa-globe"></i>
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
            <i class="fa fa-info-circle"></i> 
            No values available.
        </span>
    </div>

    <div class="flex flex-row mt-2 mb-1 items-baseline justify-between">
        <div>
            <Button v-if="!flag_selected"
                size="small"
                icon="pi pi-check"
                severity="success"
                label="Select"
                class="mr-2"
                v-tooltip.right="'Select this concept.'"
                @click="onClickSelectResult(item)">
            </Button>

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

            <div v-if="flag_enabled_value_mapping && itemValueCheck(item)"
                 class="font-bold mb-4 ml-2">
                <i class="fa fa-list"></i>
                Value Mapping
            </div>
        </div>

        <div>
            <Button v-if="flag_selected"
                size="small"
                icon="pi pi-check"
                severity="warn"
                label="Remove"
                class="mr-2"
                v-tooltip.right="'Remove this concept.'"
                @click="onClickRemoveResult(item)">
            </Button>
        </div>
    </div>

    <div v-if="flag_enabled_value_mapping && itemValueCheck(item)" 
        class="flex flex-col value-mapping">
        <div v-for="value in store.working_concept.values"
            class="value-mapping-item flex flex-row items-center">
            <div class="h-full ml-4">
                <Tag :value="value" />
            </div>
            <div class="mx-4">
                <template v-if="item.value_mapping[value]">
                    <i class="fa fa-arrow-right"></i>
                </template>
                <template v-else>
                    <i class="fa fa-times"></i>
                </template>
            </div>

            <Select v-model="item.value_mapping[value]"
                @change="onChangeValueMapping(item, value)"
                filter 
                :options="item.values"
                placeholder="Select a value"
                style="width: 20rem;"
                v-tooltip.right="'Select a value to map.'" />

            <Button v-if="item.value_mapping[value]"
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
</style>