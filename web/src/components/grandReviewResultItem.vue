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

async function onClickIntoFinal(item) {
    console.log('* clicked into final:', item);
    // Jimin.addFinalResultToWorkingConcept(item);
}

async function onClickToNext(item) {
    console.log('* clicked into next:', item);
    // Jimin.removeSelectedResultFromWorkingConcept(item);
    // check if store.working_mapping has current concept
    // if not, create a new one
    
    if (store.working_mappings[store.working_concept.concept_id] === undefined) {
        store.working_mappings[store.working_concept.concept_id] = {
            selected_results: [],
            search_results: [],
            reviewed_results: [],
            mapper_suggestion:false,
            reviewer_suggestion:false,
            status: 'mapping'
        };
    }
    store.addSelectedResultToWorkingConcept(item.selected_result);

}
</script>

<template>
<div class="result-line">
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
                    size="small"
                    icon="fa-solid fa-check-double"
                    severity="success"
                    label="Finalize"
                    class="mr-2"
                    v-tooltip.right="'Select this concept to final.'"
                    @click="onClickIntoFinal(item)">
                </Button>
                <Button
                    size="small"
                    severity="warn"
                    icon="fa-solid fa-arrow-right"
                    label="Into Next Round"
                    class="mr-2"
                    v-tooltip.right="'Select this concept to next round.'"
                    @click="onClickToNext(item)">
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
</style>