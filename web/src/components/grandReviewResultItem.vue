<script setup>
import { useDataStore } from "../DataStore";
import { Jimin } from "../Jimin";
import { ref } from "vue";
const store = useDataStore();

const props = defineProps({
    item: Object,
    item_idx: Number
});

const agree_color = ref('#5CB85C');
const disagree_color = ref('#D9534F');
const suggest_color = ref('#F0AD4E');

// helper functions
function fmtScore(score) {
    return score.toFixed(2);
};
function chartData (item){ 
        return {
        labels: ['Yes', 'No', 'Suggest'], 
        datasets: [
            {
                data: [item.agreement.length, item.disagreement.length, item.suggestion.length],
                backgroundColor: [agree_color.value, disagree_color.value, suggest_color.value]
            }
        ]
    }
};
const chartOptions = ref({
    responsive: true,
    aspectRatio: 2,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            display: false
            // position: 'right',
            // labels: {
            //     font: {
            //         size: 10
            //     },
            //     boxWidth: 10, 
            //     padding: 5,
            //     generateLabels: (chart) => {
            //         let labels = chart.data.labels;
            //         let dataset = chart.data.datasets[0].data;

            //         return labels.map((label, i) => ({
            //             text: `${label}: ${dataset[i]}`,
            //             fillStyle: chart.data.datasets[0].backgroundColor[i],
            //             hidden: chart.getDatasetMeta(0).data[i].hidden,
            //             index: i
            //         }));
            //     }
            // }
        }
    }
});

function inWorking(item) {
    return store.working_mappings[store.working_concept.concept_id].selected_results
        .find(r => JSON.stringify(r) === JSON.stringify(item.selected_result)) !== undefined;
}

async function onClickExclude(item) {
    console.log('* clicked onClickExclude:', item);
    // remove from selected_results
    store.removeSelectedResultFromWorkingConcept(item.selected_result);
    let ret = await Jimin.updateSelectedResults(
        store.working_concept.concept_id,
        store.working_file.round.length,
        store.working_mappings[store.working_concept.concept_id].selected_results
    );
        console.log('* updated selected results:', ret);

        // show a message
        store.msg(ret.message);
}

async function onClickInclude(item) {
    console.log('* clicked onClickInclude:', item);

    store.addSelectedResultToWorkingConcept(item.selected_result);
    
    let ret = await Jimin.updateSelectedResults(
        store.working_concept.concept_id,
        store.working_file.round.length,
        store.working_mappings[store.working_concept.concept_id].selected_results
    );

    store.addSelectedResultToWorkingConcept(item.selected_result);
    console.log('* updated selected results:', ret);

    // show a message
    store.msg(ret.message);

}

// popover related
const popover_yes = ref();
const togglePopoverYes = (event) => {
    popover_yes.value.toggle(event);
};

const popover_no = ref();
const togglePopoverNo = (event) => {
    popover_no.value.toggle(event);
};

const popover_suggest = ref();
const togglePopoverSuggest = (event) => {
    popover_suggest.value.toggle(event);
};
</script>

<template>
<div class="result-line"
    :class="{ 'disabled-term': store.working_concept.final }"
    >
    <div class="result-tags">
        <div class="flex flex-row">
            <Badge :value="fmtScore(item.selected_result.score)" 
                class="mr-1 badge-score"
                severity="info" />
            <Badge :value="item.selected_result.term_source" severity="info" />
        </div>

        <div>

        </div>
    </div>
    <div class="result-name">
        <div class="flex items-center">
            <div class="font-bold text-lg">
                {{ item.selected_result.term }}
            </div>
            <Divider layout="vertical" class="!mx-2" />
            <div class="text-base">
                <a :href="'https://cde.nlm.nih.gov/deView?tinyId=' + item.selected_result.term_id"
                    title="Open this CDE in NIH CDE Browser in a new tab."
                    target="_blank">
                    <font-awesome-icon :icon="['fa', 'globe']" />
                    {{ item.selected_result.term_id }}
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
        {{ item.selected_result.description }}
    </div>
    <div class="mt-4">
        <span class="font-bold text-lg mb-2">Statistics:</span>
        <div class="flex flex-row mt-2 mb-1 items-baseline justify-between">
            <div class="flex flex-row">
                <div class="flex flex-col justify-center items-center">
                    <span class="font-bold text-lg">Distribution</span>
                    <Chart type="pie" :data="chartData(item)" :options="chartOptions" class="md:w-[15em] h-[8em]" />
                </div>
                <div class="ml-4 flex flex-col justify-center items-center">
                    <!-- Agreement info component -->
                    <div class="flex flex-row items-center">
                        <Button
                            size="small"
                            :disabled="item.agreement.length === 0"
                            severity="secondary"
                            :style="{ backgroundColor: agree_color, color: 'white' }"
                            label="Yes"
                            class="mb-1 text-xs px-2 py-1 h-6 w-20 hover:brightness-110"
                            v-tooltip.top="'Click to view detail.'"
                            @click="togglePopoverYes">
                        </Button>
                        
                        <Popover ref="popover_yes">
                            <div class="flex flex-col">
                                <span class="font-bold text-lg">Agree: {{ item.agreement.length }}</span>
                                <span class="text-sm">Details:</span>
                                <div class="card">
                                    <DataTable :value="item.agreement" tableStyle="min-width: 30rem">
                                        <Column field="name" header="Name"></Column>
                                        <Column field="email" header="Email"></Column>
                                        <Column field="comment" header="Comment"></Column>
                                    </DataTable>
                                </div>
                            </div>
                        </Popover>
                        <span class="ml-2"><font-awesome-icon :icon="['fas', 'user']" />: {{ item.agreement.length }}</span>
                    </div>
                    <!-- Dissagree info component -->
                    <div class="flex flex-row items-center">
                        <Button
                            size="small"
                            :disabled="item.disagreement.length === 0"
                            severity="secondary"
                            :style="{ backgroundColor: disagree_color, color: 'white' }"
                            label="No"
                            class="mb-1 text-xs px-2 py-1 h-6 w-20 hover:brightness-110"
                            v-tooltip.top="'Click to view detail.'"
                            @click="togglePopoverNo">
                        </Button>
                        <Popover ref="popover_no">
                            <div class="flex flex-col">
                                <span class="font-bold text-lg">Dissagree: {{ item.disagreement.length }}</span>
                                <span class="text-sm">Details:</span>
                                <div class="card">
                                    <DataTable :value="item.disagreement" tableStyle="min-width: 30rem">
                                        <Column field="name" header="Name"></Column>
                                        <Column field="email" header="Email"></Column>
                                        <Column field="comment" header="Comment"></Column>
                                    </DataTable>
                                </div>
                            </div>
                        </Popover>
                        <span class="ml-2"><font-awesome-icon :icon="['fas', 'user']" />: {{ item.disagreement.length }}</span>
                    </div>
                    <!-- Suggest info component -->
                    <div class="flex flex-row items-center">
                        <Button
                            size="small"
                            :disabled="item.suggestion.length === 0"
                            severity="secondary"
                            :style="{ backgroundColor: suggest_color, color: 'white' }"
                            label="Suggest"
                            class="mb-1 text-xs px-2 py-1 h-6 w-20 hover:brightness-110"
                            v-tooltip.top="'Click to view detail.'"
                            @click="togglePopoverSuggest">
                        </Button>
                        <Popover ref="popover_suggest">
                            <div class="flex flex-col">
                                <span class="font-bold text-lg">Suggest: {{ item.suggestion.length }}</span>
                                <span class="text-sm">Details:</span>
                                <div class="card">
                                    <DataTable :value="item.suggestion" tableStyle="min-width: 18rem">
                                        <Column field="name" header="Name"></Column>
                                        <Column field="email" header="Email"></Column>
                                    </DataTable>
                                </div>
                            </div>
                        </Popover>
                        <span class="ml-2"><font-awesome-icon :icon="['fas', 'user']" />: {{ item.suggestion.length }}</span>
                    </div>
                </div>
            </div>
            <div>
                <Button
                    v-if="inWorking(item)"
                    size="small"
                    icon="fa-solid fa-xmark"
                    severity="danger"
                    label="Exclude"
                    class="mr-2"
                    v-tooltip.right="'Exclude this concept to next reviewing round.'"
                    @click="onClickExclude(item)">
                </Button>
                <Button
                    v-if="!inWorking(item)"
                    size="small"
                    severity="warn"
                    icon="fa-solid fa-arrows-rotate"
                    label="Include"
                    class="mr-2"
                    v-tooltip.right="'Select this concept to next round.'"
                    @click="onClickInclude(item)">
                </Button>
            </div>
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


.disabled-term {
    pointer-events: none;
    opacity: 0.6; 
}

</style>