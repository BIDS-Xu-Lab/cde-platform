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
            <div>
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
        Question Text:
        {{ item.description }}
    </div>

    <div class="flex flex-row mt-2 mb-1">

        <div>
            <Button v-if="flag_selected"
                size="small"
                icon="pi pi-check"
                severity="warn"
                label="Remove"
                class="mr-2 btn-mini"
                v-tooltip.right="'Remove this concept.'"
                @click="onClickRemoveResult(item)">
            </Button>

            <Button v-if="!flag_selected"
                size="small"
                icon="pi pi-check"
                severity="success"
                label="Select"
                class="mr-2 btn-mini"
                v-tooltip.right="'Select this concept.'"
                @click="onClickSelectResult(item)">
            </Button>
        </div>

        <Divider layout="vertical" class="!mx-2" />
        
        <div v-if="flag_enabled_value_mapping">
            <Button
                size="small"
                icon="pi pi-list"
                label="Value Mapping"
                severity="success"
                class="btn-mini"
                v-tooltip.right="'Map values for this concept.'"
                @click="store.showGuide()">
            </Button>
        </div>
        <div v-else>
            <Button
                size="small"
                icon="pi pi-list"
                label="Show values"
                severity="secondary"
                class="btn-mini"
                v-tooltip.right="'Show values for this concept.'"
                @click="store.showGuide()">
            </Button>
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