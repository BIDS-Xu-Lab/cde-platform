<script setup>
import { useDataStore } from "../DataStore";
import { Jimin } from "../Jimin";
import { ref } from "vue";
const store = useDataStore();

const props = defineProps({
    item: Object,
    item_idx: Number
});

const agree_color = ref('#91ff85');
const disagree_color = ref('#ff4383');
const suggest_color = ref('#ffac43');

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
            position: 'right',
            labels: {
                font: {
                    size: 10
                },
                boxWidth: 10, 
                padding: 5,
                generateLabels: (chart) => {
                    let labels = chart.data.labels;
                    let dataset = chart.data.datasets[0].data;

                    return labels.map((label, i) => ({
                        text: `${label}: ${dataset[i]}`,
                        fillStyle: chart.data.datasets[0].backgroundColor[i],
                        hidden: chart.getDatasetMeta(0).data[i].hidden,
                        index: i
                    }));
                }
            }
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
            <div class="flex flex-col justify-center items-center">
                <span class="font-bold text-lg">Number of reviewer</span>
                <Chart type="pie" :data="chartData(item)" :options="chartOptions" class="md:w-[10em] h-[5em]" />
            </div>
            <div>
                <Button
                    v-if="inWorking(item)"
                    size="small"
                    icon="fa-solid fa-xmark"
                    severity="danger"
                    label="Exclude"
                    class="mr-2"
                    v-tooltip.right="'Select this concept to final.'"
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