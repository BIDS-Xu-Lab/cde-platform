<script setup>
import { useDataStore } from '../DataStore';
import { onMounted, ref } from 'vue';
import { Button } from 'primevue';

import * as CDEHelper from '../CDEHelper';
import { Jimin } from '../Jimin';
import SearchResultItem from '../components/SearchResultItem.vue';
import MappingReviewMenuItem from '../components/MappingReviewMenuItem.vue';

const store = useDataStore();

async function onClickRefreshList() {
    console.log('* clicked Refresh List');

    // load source data
    let sources = await Jimin.getSources();

    store.msg('Loaded ' + sources.length + ' sources.');

    // update store
    store.mapping.sources = sources.map((item) => {
        return {
            name: item,
            code: item
        };
    });
}

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
// {
//     label: 'Name',
//     code: 'name',
//     items: [
//         { label: 'Name ascent', value: 'asc' },
//         { label: 'Name descent', value: 'desc' },
//     ]
// },
// {
//     label: 'Description',
//     code: 'description',
//     items: [
//         { label: 'Description ascent', value: 'asc' },
//         { label: 'Description descent', value: 'desc' },
//     ]
// },
];


const sort_order_options = [
    { name: 'Descent', code: 'desc' },
    { name: 'Ascent', code: 'asc' }
];

async function onClickConcept(concept) {
    console.log('* clicked concept:', concept);
    store.working_concept = concept;
}

function fmtScore(score) {
    return score.toFixed(2);
}

///////////////////////////////////////////////////////////
// Selection related
///////////////////////////////////////////////////////////

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

const selected_results_panel = ref();
const search_results_panel = ref();

onMounted(() => {
    console.log('* mounted MappingView');

    // load source data
    if (store.mapping.sources.length == 0) {
        onClickRefreshList();
    }
});
</script>

<template>
    <MappingReviewMenuItem :view_mode="'mapping'" />

<!-- main -->
<div class="main flex-row">

<!-- concept list -->
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
                    :class="{ 'working-term': store.isWorkingConcept(item) }"
                    @click="onClickConcept(item)">
                    <div class="term-name">
                        <div class="mr-1">
                            <template v-if="store.hasSelectedResults(item)">
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
                    </div>
                    <div class="term-concept">
                        <div class="flex flex-col text-small">
                            <div class="flex items-center">
                                <template v-if="store.hasSelectedResults(item)">
                                    <i class="fa-solid fa-arrow-right-to-bracket mr-1"></i>
                                    {{ store.getSelectedResults(item).length }} Mapped Recommended.
                                </template>
                                <template v-else>
                                    <i class="fa fa-exclamation-triangle mr-1"></i>
                                    Not Mapped.
                                </template>
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

<div class="flex flex-col w-full h-full result-list">

    <Panel ref="search_results_panel"
        class="w-full">
        <template #header>
            <div class="w-full flex justify-between items-center">
                <div class="flex">
                    <div class="flex-col">
                        <div class="text-lg font-bold">
                            <i class="fa-solid fa-cubes"></i>
                            CDE Mappings
                            <span v-if="store.working_concept">
                                for 
                                <i>{{ store.working_concept?.term }}</i>
                            </span>
                        </div>
                        <div class="panel-subtitle text-sm">
                            <template v-if="store.working_mappings[store.working_concept?.concept_id]?.search_results.length > 0">
                                <b>{{ store.working_mappings[store.working_concept?.concept_id]?.search_results.length }}</b>
                                potential matches
                                | 
                                <b>{{ store.working_mappings[store.working_concept?.concept_id]?.selected_results.length }}</b>
                                selected
                            </template>
                            <template v-else>
                                &nbsp;
                            </template>
                        </div>
                    </div>
                </div>
                
                <div class="flex justify-end mr-2" 
                    style="height: 2rem; line-height: 1rem;">
                    <InputText v-model="store.mapping.filter_results_by"
                        type="text" 
                        placeholder="Filter keyword ..."
                        class="term-filter"/>
                    
                    <Divider layout="vertical" class="!mx-2" />

                    <Select v-model="store.mapping.sort_results_by" 
                        :options="sort_results_options" 
                        optionLabel="name" 
                        optionValue="name" 
                        placeholder="Sort by" 
                        class="term-sort mr-1"/>

                    <Select v-model="store.mapping.sort_results_order_by" 
                        :options="sort_order_options" 
                        optionLabel="name" 
                        placeholder="Order by" 
                        class="term-sort"/>

                </div>
            </div>
        </template>

        <div class="result-list-scroller"
            :style="{ height: 'calc(100vh - 19rem)' }">

            <!-- selected list -->
            <template v-if="store.working_mappings[store.working_concept?.concept_id]?.selected_results.length > 0">
            <div class="selected-results-section">

                <div class="text-lg font-bold mb-4">
                    <i class="fa-solid fa-check-double"></i>
                    Selected Results
                    ({{ store.working_mappings[store.working_concept?.concept_id]?.selected_results.length }})
                </div>
                
                <template v-for="item, item_idx in store.working_mappings[store.working_concept?.concept_id]?.selected_results">
                    <SearchResultItem :item="item" 
                        :flag_selected="true"
                        :flag_enabled_value_mapping="true"
                        :item_idx="item_idx" 
                        :flag_submitted="CDEHelper.checkSubmitStatus()"
                        />
                </template>

            </div>
            <Divider />
            </template>

            <!-- result list -->
            <template v-if="store.working_mappings[store.working_concept?.concept_id]?.search_results.length > 0">

            <div class="text-lg font-bold mt-4">
                <i class="fa-solid fa-list-ul"></i>
                Search Results
                ({{ store.working_mappings[store.working_concept?.concept_id]?.search_results.length - store.working_mappings[store.working_concept?.concept_id]?.selected_results.length }})
            </div>
            <template v-for="item, item_idx in store.working_mappings_search_results_without_selected">
                <SearchResultItem :item="item" 
                    :flag_selected="false"
                    :flag_enabled_value_mapping="false"
                    :item_idx="item_idx" 
                    :flag_submitted="CDEHelper.checkSubmitStatus()"
                    />
            </template>

            </template>
            <template v-else>
                <div class="">
                    <i class="fa-solid fa-info-circle"></i>
                    No search results
                </div>
            </template>
                
        </div>
    </Panel>
</div>

</div>

</template>

<style scoped>
.select-sources {
    width: 10rem;
}

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

.selected-results-section {
    background-color: var(--bg-color-selected);
}

.result-list-scroller {
    width: calc(100% + 1rem);
    overflow-y: auto;
}

</style>