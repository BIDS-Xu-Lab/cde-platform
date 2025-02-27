<script setup>
import { useDataStore } from '../DataStore';
import { computed, onMounted, ref } from 'vue';
import { Button, Popover, ProgressBar } from 'primevue';
import { Jimin } from '../Jimin';

const store = useDataStore();

const props = defineProps({
    view_mode: String
});

const sort_terms_options = [
    {
        label: 'Name',
        code: 'name',
        items: [
            { label: 'Term ascent', value: 'term|asc', icon: ['fa', 'arrow-down-az'] },
            { label: 'Term descent', value: 'term|desc', icon: ['fa', 'arrow-down-az'] },
        ]
    },
    {
        label: 'Description',
        code: 'description',
        items: [
            { label: 'Description ascent', value: 'description|asc', icon: ['fa', 'arrow-down-az'] },
            { label: 'Description descent', value: 'description|desc', icon: ['fa', 'arrow-down-az'] },
        ]
    },
];

function onChangeSortTerms() {
    console.log('* changed Sort Terms:', store.mapping.sort_terms_by);

    if (store.mapping.sort_terms_by == null) {
        return;
    }
}

const sort_results_options = [
{ name: 'Name', code:'name' },
{ name: 'Score', code:'score' },

];
async function onClickConcept(concept) {
    console.log('* clicked concept:', concept);
    store.working_concept = concept;
}

const visible_dialog_propose_cde = ref(false);

function onclickProposeCDE(concept) {
    console.log('* clicked propose CDE', concept);
    visible_dialog_propose_cde.value = true;
}

async function onClickSuggest() {
    console.log('* clicked suggest', store.working_concept);
    visible_dialog_propose_cde.value = false;
    let ret = await Jimin.suggestConceptToCDE(store.working_concept.concept_id, props.view_mode);
    // if ret.success, then update all mappings
    if (ret.success) {
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
    }
    console.log(ret.message);
}

const visible_dialog_final_decision = ref(false);
function onClickFinal() {
    console.log('* clicked final');
    visible_dialog_final_decision.value = true;
}

async function onClickYesToFinal() {
    console.log('* clicked yes to final');
    console.log('store.working_concept:', store.working_concept);
    visible_dialog_final_decision.value = false;
    let ret = await Jimin.finalizeConcept(store.working_concept.concept_id);
    if (ret.success) {
        store.working_concept.final = true;
    }
    store.working_concept = null;
    store.msg(ret.message);
}

function agreeConsistency(item) {
    const mapping = store.grand_review_data.find(mapping => mapping.concept_id === item.concept_id);
    if (!mapping) return 0;

    const { total, agree } = mapping.selected_results.reduce((acc, result) => {
        acc.total += result.agreement.length + result.disagreement.length + result.suggestion.length;
        acc.agree += result.agreement.length;
        return acc;
    }, { total: 0, agree: 0 });

    return total === 0 ? 0 : (agree / total) * 100;
}

function disabledByReview(item) {
    // if selected_results greater than reviewed_results, then disable
    if (store.working_mappings[item.concept_id]?.selected_results.length > store.working_mappings[item.concept_id]?.reviewed_results.length) {
        return true;
    }
    // Then, count the number of disagreement in reviewed_results, where count how many reviewd_result['agreement'] is false (note: may null but not false, only count the false)
    const disagreement = store.working_mappings[item.concept_id]?.reviewed_results.reduce((acc, result) => {
        if (result.agreement === false) {
            return acc + 1;
        }
        return acc;
    }, 0);
    // if disagreement is equal to reviewed_results, then disable
    if (disagreement === store.working_mappings[item.concept_id]?.reviewed_results.length) {
        return false;
    }
    return true;
}
</script>
<template>
    <div>
        <Panel class="h-full term-list mr-2">
            <template #header>
                <div class="w-full flex justify-between">
                    <div class="flex">
                        <div class="flex-col">
                            <div class="text-lg font-bold">
                                <font-awesome-icon icon="fa-solid fa-list" />
                                Concept List
                            </div>
                            <div class="panel-subtitle text-sm">
                                <b>{{ store.n_mapped_concepts_in_working_file }}</b>
                                /
                                {{ store.working_file_concepts.length }}  
                                mapped
                            </div>
                        </div>
                    </div>
                    
                    <div class="flex justify-end" style="height: 2rem; line-height: 1rem;">
                        <InputText v-model="store.mapping.filter_terms_by"
                            type="text" 
                            placeholder="Filter keyword ..."
                            style="width: 9rem;" />

                        <Divider layout="vertical" class="!mx-2" />

                        <Select v-model="store.mapping.sort_terms_by" 
                            @change="onChangeSortTerms"
                            :options="sort_terms_options" 
                            optionGroupLabel="label"
                            optionGroupChildren="items"
                            optionLabel="label" 
                            optionValue="value"
                            placeholder="Sort by" 
                            showClear
                            scrollHeight="25rem"
                            style="width: 12rem;">
                            <template #optiongroup="slotProps">
                                <div class="flex items-center">
                                    <div class="mr-2">
                                        <font-awesome-icon icon="fa-solid fa-circle" />
                                    </div>
                                    <div>{{ slotProps.option.label }}</div>
                                </div>
                            </template>
                            <template #option="slotProps">
                                <div class="flex items-center">
                                    <div class="mx-1">
                                        <i class="fa-solid fa-minus"></i>
                                    </div>
                                    <div>{{ slotProps.option.label }}</div>
                                </div>
                            </template>
                        </Select>

                    </div>
                </div>
            </template>

            <div class="term-list-box">
                <div class="term-list-scroller"
                    :style="{ height: 'calc(100vh - 18rem)'}">
                    <template v-for="item in store.filtered_working_file_concepts">
                        <div class="term-line"
                            :class="{ 'working-term': store.isWorkingConcept(item)}"
                            @click="onClickConcept(item)">
                            <div class="term-name">
                                <div class="mr-1">
                                    <template v-if="store.hasSelectedResults(item) || store.working_mappings[item.concept_id]?.mapper_suggestion || store.working_mappings[item.concept_id]?.reviewer_suggestion">
                                        <Tag :value="item.id + 1" severity="success" />
                                    </template>
                                    <template v-else-if="store.hasSearchResults(item)">
                                        <Tag :value="item.id + 1" severity="info" />
                                    </template>
                                    <template v-else>
                                        <Tag :value="item.id + 1" severity="contrast" />
                                    </template>
                                </div>
                                <div :class="{ 'font-bold': store.isWorkingConcept(item) }">
                                    {{ item.term }}
                                </div>
                                <span v-if="item.final" class="text-lg ml-10 font-bold">
                                        <i class="fa-solid fa-flag-checkered"></i>
                                        Finalized
                                </span>
                            </div>
                            <div class="term-concept">
                                <div v-if="view_mode !== 'grand_review'"
                                    class="flex flex-col text-small">
                                    <div class="flex items-center">
                                        <template v-if = "store.working_mappings[item.concept_id]?.selected_results.length === 0 & store.working_mappings[item.concept_id]?.mapper_suggestion || store.working_mappings[item.concept_id]?.reviewer_suggestion">
                                            <i class="fa-solid fa-arrow-up-from-bracket mr-1"></i>
                                            Suggest as CDE.
                                        </template>

                                        <template v-else-if="store.hasSelectedResults(item)">
                                            <i class="fa-solid fa-arrow-right-to-bracket mr-1"></i>
                                            {{ store.getSelectedResults(item).length }} Mapped Recommended.
                                        </template>

                                        <template v-else>
                                            <i class="fa fa-exclamation-triangle mr-1"></i>
                                            Not Mapped.
                                        </template>
                                    </div>
                                </div>
                                <div v-else class="flex flex-row items-center text-small">
                                    <span class="mr-2">Consistency:</span>
                                    <div style="width: 100px;">
                                        <ProgressBar :value="agreeConsistency(item)"></ProgressBar>
                                    </div>
                                </div>
                                <div class="mr-1">
                                    <Button v-if="false"
                                        size="small"
                                        icon="pi pi-times"
                                        label="De-select"
                                        severity="warn"
                                        class="mr-1 btn-mini btn-de-select"
                                        v-tooltip.right="'De-select this concept.'"
                                        @click="store.showGuide()">
                                    </Button>
                                </div>
                            </div>
                            <div class="term-detail">
                                <b>
                                    Description:
                                </b>
                                {{ item.description }}
                            </div>
                            <div class="flex justify-between">
                                <div>
                                    <b>
                                        Values:
                                    </b>
                                    <span v-if="item.values?.length > 0">
                                        {{ item.values.length }} values.
                                    </span>
                                    <span v-else class="text-sm">
                                        <font-awesome-icon icon="fa-solid fa-info-circle" />
                                        No values available.
                                    </span>
                                </div>
                                <div v-if="view_mode === 'mapping'"
                                    :class="{ 'disabled-term': item.final }">
                                    <Button 
                                        class="btn-mini mr-2"
                                        :disabled="store.working_concept !== item || store.working_mappings[item.concept_id]?.status === 'mapped' || store.working_mappings[item.concept_id]?.selected_results.length > 0"
                                        v-if="!store.working_mappings[item.concept_id]?.mapper_suggestion" 
                                        severity="warn"
                                        v-tooltip.bottom="'Recommend this concept as CDE.'"
                                        @click="onclickProposeCDE(item)">
                                        <i class="fa-solid fa-arrow-up-from-bracket"></i>
                                        Propose CDE
                                    </Button>
                                    <Button 
                                        class="btn-mini mr-2"
                                        :disabled="store.working_concept !== item|| store.working_mappings[item.concept_id]?.status === 'mapped'"
                                        v-if="store.working_mappings[item.concept_id]?.mapper_suggestion" 
                                        severity="danger"
                                        v-tooltip.bottom="'Deselect this concept as CDE.'"
                                        @click="onClickSuggest()">
                                        <i class="fa-solid fa-minus"></i>
                                        Recall propose
                                    </Button>
                                </div>
                                <div v-if="view_mode === 'reviewing'"
                                    :class="{ 'disabled-term': item.final }">
                                    <div class="flex flex-col items-end" v-if="store.working_mappings[item.concept_id].mapper_suggestion">
                                        <p class = "mb-2 mr-2">Suggested as CDE by mapper</p>
                                        <Button 
                                            class="btn-mini mr-2"
                                            :disabled="store.working_concept !== item || store.working_mappings[item.concept_id]?.status === 'reviewed'"
                                            v-if="store.working_mappings[item.concept_id]?.reviewer_suggestion" 
                                            severity="danger"
                                            v-tooltip.bottom="'Disagree this to CDE.'"
                                            @click="onClickSuggest()">
                                            <i class="fa-solid fa-times"></i>
                                            Disagree
                                        </Button>
                                        <Button 
                                            class="btn-mini mr-2"
                                            :disabled="store.working_concept !== item || store.working_mappings[item.concept_id]?.status === 'reviewed' || disabledByReview(item)"
                                            v-if="!store.working_mappings[item.concept_id]?.reviewer_suggestion" 
                                            severity="info"
                                            v-tooltip.bottom="'Recall disagree.'"
                                            @click="onClickSuggest()">
                                            <i class="fa-solid fa-rotate-left"></i>
                                            Recall
                                        </Button>
                                    </div>
                                    <div v-else>
                                        <Button 
                                            class="btn-mini mr-2"
                                            :disabled="store.working_concept !== item || store.working_mappings[item.concept_id]?.status === 'reviewed' || disabledByReview(item)"
                                            v-if="!store.working_mappings[item.concept_id]?.reviewer_suggestion" 
                                            severity="warn"
                                            v-tooltip.bottom="'Recommend this concept as CDE.'"
                                            @click="onclickProposeCDE(item)">
                                            <i class="fa-solid fa-arrow-up-from-bracket"></i>
                                            Propose CDE
                                        </Button>
                                        <Button 
                                            class="btn-mini mr-2"
                                            :disabled="store.working_concept !== item || store.working_mappings[item.concept_id]?.status === 'reviewed'"
                                            v-if="store.working_mappings[item.concept_id]?.reviewer_suggestion" 
                                            severity="danger"
                                            v-tooltip.bottom="'Deselect this concept as CDE.'"
                                            @click="onClickSuggest()">
                                            <i class="fa-solid fa-minus"></i>
                                            Recall propose
                                        </Button>
                                    </div>
                                </div>
                                <div v-if="view_mode ==='grand_review'">
                                    <Button 
                                        class="btn-mini mr-2"
                                        :disabled="store.working_concept !== item || store.working_concept.final"
                                        v-if:="!item.final"
                                        severity="info"
                                        v-tooltip.bottom="'Set this concept to Finalized.'"
                                        @click="onClickFinal()">
                                        <i class="fa-solid fa-flag-checkered"></i>
                                        Set to Final
                                    </Button>
                                </div>
                            </div>

                            <div class="term-additional mt-2">
                                <Accordion value="1" class="w-full px-2" :unstyled="true">
                                    <AccordionPanel value="0">
                                        <AccordionHeader>
                                            <i class="fa fa-info-circle mr-1"></i>
                                            Detailed Information
                                        </AccordionHeader>
                                        <AccordionContent>
                                            <template v-for="key in Object.keys(item)">
                                                <div v-if="['id', 'term', 'description', 'user_id', 'project_id', 'concept_id', 'file_id', 'values'].indexOf(key) < 0" 
                                                    class="flex justify-between">
                                                    <div class="font-bold">{{ key }}</div>
                                                    <div>{{ item[key] }}</div>
                                                </div>
                                                <div v-else-if="key == 'values'">
                                                    <div class="font-bold">
                                                        Values
                                                    </div>
                                                    <div>
                                                        <template v-for="value in item[key]">
                                                            <div class="flex justify-start">
                                                                <div class="ml-2">
                                                                    <i class="fa-regular fa-circle-dot"></i>
                                                                    {{ value }}
                                                                </div>
                                                            </div>
                                                        </template>
                                                    </div>
                                                </div>
                                            </template>
                                        </AccordionContent>
                                    </AccordionPanel>
                                </Accordion>    

                            </div>
                        </div>
                    </template>
                </div>

            </div>
        </Panel>
    </div>
    <Dialog v-model:visible="visible_dialog_propose_cde" 
        modal
        header="Are you sure you want to suggest this concept to CDE?"
        width="400px" 
        :closable="false">
        <div class="flex flex-col gap-4">
            
            <div class="flex flex-row justify-end gap-2">
                <Button 
                severity="secondary" 
                @click="visible_dialog_propose_cde = false">
                <font-awesome-icon :icon="['fas', 'xmark']" />
                No
                </Button>

                <Button 
                severity="primary" 
                @click="onClickSuggest()">
                <font-awesome-icon :icon="['fas', 'arrow-right']" />
                    suggest
                </Button>
            </div>
        </div>
    </Dialog>
    <Dialog v-model:visible="visible_dialog_final_decision" 
        modal
        header="Are you sure you want this concept to Final?"
        width="400px" 
        :closable="false">
        <div class="flex flex-col gap-4">
            <p>You cannot modify this concept after it has been finalized.</p>
            <div class="flex flex-row justify-end gap-2">
                <Button 
                severity="secondary" 
                @click="visible_dialog_final_decision = false">
                <font-awesome-icon :icon="['fas', 'xmark']" />
                No
                </Button>
                <Button 
                severity="primary" 
                @click="onClickYesToFinal()">
                <font-awesome-icon :icon="['fas', 'arrow-right']" />
                    Yes
                </Button>
            </div>
        </div>
    </Dialog>
</template>
<style scoped>
.term-list {
    width: 500px;
    min-width: 460px;
    height: 100%;
}

.result-list {
    width: calc(100% - 500px);
}
.term-list-scroller {
    width: calc(100% + 1rem);
    overflow-y: auto;
}
.term-line {
    width: 100%;
    border-bottom: 1px solid var(--bd-color);
    padding: 0.5rem 0;
    display: flex;
    flex-direction: column;
    cursor: pointer;
}
.term-line:hover {
    background-color: var(--bg-color-menu-hover);
}
.term-name {
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: top;
    font-size: 1.2rem;
    line-height: 1.5rem;
}
.term-detail {
    line-height: 1.2rem;
    margin: 0.5rem 0;
}
.term-concept {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    align-items: center;
}
.term-additional {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.working-term {
    background-color: var(--bg-color-selected);
}


.result-list-scroller {
    width: calc(100% + 1rem);
    overflow-y: auto;
}

.disabled-term {
    pointer-events: none;
    opacity: 0.5; 
}
</style>