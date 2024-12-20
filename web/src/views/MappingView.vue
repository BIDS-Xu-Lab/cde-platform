<script setup>
import ToggleSwitch from 'primevue/toggleswitch';
import VirtualScroller from 'primevue/virtualscroller';
import Badge from 'primevue/badge';

import { useDataStore } from '../DataStore';
import { onMounted, ref } from 'vue';
import { useElementSize } from '@vueuse/core';
import { Button } from 'primevue';

import * as CDEHelper from '../CDEHelper';
import { Jimin } from '../Jimin';
import SearchResultItem from '../components/SearchResultItem.vue';

const store = useDataStore();
const prograss_visible = ref(false);
const prograss_value = ref(0);
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

async function onChangeSource() {
    console.log('* changed Source:', store.mapping.selected_source);

    // load collections
    let collections = await Jimin.getCollectionsBySource(store.mapping.selected_source);

    store.msg('Loaded ' + collections.length + ' collections.');

    // update store
    store.mapping.collections = collections.map((item) => {
        return {
            name: item,
            code: item
        };
    });
}

async function onClickSearch() {
    console.log('* clicked Search ');
    if(store.mapping.selected_source == null) {
        store.msg('Please select a source to search.', 'error', 'error');
        return;
    }
    if (store.working_concept == null) {
        store.msg('Please select a concept to search.', 'error', 'error');
        return;
    }

    // search CDEs on the working concept
    let results = await Jimin.search(
        store.mapping.selected_source,
        store.mapping.selected_collections,
        [store.working_concept],
        store.features.embedding_search.enabled,
        false,
        false,
        100
    );

    console.log('* search results:', results);

    // check whether store.working_concept.id is in store.working_mappings
    if (store.working_concept.concept_id in store.working_mappings) {
        store.working_mappings[store.working_concept.concept_id].search_results = results[0];
    } else {
        store.working_mappings[store.working_concept.concept_id] = {
            search_results: results[0],
            selected_results: []
        }
    }
}

async function onClickSearchAll() {
    console.log('* clicked Search All');
    if(store.mapping.selected_source == null) {
        store.msg('Please select a source to search.','error', 'error');
        return;
    }
    prograss_visible.value = true;
    // for each concept in the working_file_concepts
    // search CDEs on the working concept
    for (let i=0; i < store.working_file_concepts.length; i++) {
        prograss_value.value = i + 1;
        let concept = store.working_file_concepts[i];

        // search CDEs on the working concept
        let results = await Jimin.search(
            store.mapping.selected_source,
            store.mapping.selected_collections,
            [concept],
            store.features.embedding_search.enabled,
            false,
            false,
            100
        );

        console.log('* search results for ', i, results);

        // check whether store.working_concept.id is in store.working_mappings
        if (concept.concept_id in store.working_mappings) {
            store.working_mappings[concept.concept_id].search_results = results[0];
        } else {
            store.working_mappings[concept.concept_id] = {
                search_results: results[0],
                selected_results: []
            }
        }
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    // sleep 1 sec let animation can be shown
    
    prograss_visible.value = false;
    prograss_value.value = 0;
    store.msg('Searched all results.');
}

async function onClickSaveClose() {
    console.log('* clicked Save and Close');

    // save the current mappings to the server
    // just sleep 3 seconds
    store.msg('Saved the current mappings.');

    // clear working mappings
    store.clearMappingData();

    // switch to the project view
    store.changeView('project_list');
}

function onClickDownload() {
    console.log('* clicked Download');
}

const downloadOptions = [{
    icon: 'pi pi-file',
    label: 'JSONL Format',

    command: () => {
        store.toast.add({ severity: 'success', summary: 'Downloaded successfully!', detail: 'Downloaded all data into a single JSONL file.', life: 3000 });
    }
},
{
    icon: 'pi pi-file',
    label: 'YAML Format',
    command: () => {
        store.toast.add({ severity: 'success', summary: 'Downloaded successfully!', detail: 'Downloaded all data into a single YAML file.', life: 3000 });
    }
},
{
    icon: 'pi pi-file-excel',
    label: 'TSV Format',
    title: "Download all data into a single TSV file.",
    command: () => {
        store.toast.add({ severity: 'success', summary: 'Downloaded successfully!', detail: 'Downloaded all data into a single TSV file.', life: 3000 });
    }
},
{
    separator: true
},
{
    label: 'Raw JSON Format',
    command: () => {
        store.toast.add({ severity: 'success', summary: 'Downloaded successfully!', detail: 'Downloaded all data into a single JSON file.', life: 3000 });
    }
}
];

function onClickRerank() {
    console.log('* clicked Re-rank');
}

function onClickValueLinking() {
    console.log('* clicked Value Linking');
}

const sort_term_options = [
    { name: 'Name', code: 'name' },
    { name: 'Type', code: 'type' },
    { name: 'Status', code: 'status' }
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
<div class="menu">
    <div class="menu-group !ml-2">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Refresh list.'"
                @click="onClickRefreshList">
                <i class="fa-solid fa-rotate menu-icon"></i>
                <span>
                    Refresh
                </span>
            </Button>

            <div class="flex flex-col mr-2">
                <label class="text-sm">
                    <i class="fa fa-database"></i>
                    Sources
                </label>
                <Select v-model="store.mapping.selected_source" 
                    :options="store.mapping.sources" 
                    @change="onChangeSource"
                    variant="in"
                    filter 
                    optionLabel="name" 
                    optionValue="code" 
                    placeholder="Select a data source" 
                    class="select-sources">
                    <template #header>
                        <div class="font-bold px-3">Available Sources</div>
                    </template>
                </Select>
            </div>

            <div class="flex flex-col">
                <label class="text-sm" for="">
                    <i class="fa-solid fa-book-bookmark"></i>
                    Collections
                </label>
                <MultiSelect v-model="store.mapping.selected_collections" 
                    :options="store.mapping.collections" 
                    variant="in"
                    filter 
                    optionLabel="name" 
                    optionValue="code" 
                    placeholder="Select data collections" 
                    class="select-sources">
                    <template #header>
                        <div class="font-bold px-3">Available Collections</div>
                    </template>
                </MultiSelect>
            </div>

            <Button text
                class="menu-button"
                v-tooltip.bottom="'Search CDEs for the current selected concept.'"
                @click="onClickSearch">
                <i class="fa-solid fa-magnifying-glass menu-icon"></i>
                <span>
                    Search
                </span>
            </Button>
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Search CDEs for all terms.'"
                @click="onClickSearchAll">
                <i class="fa-brands fa-searchengin menu-icon"></i>
                <span>
                    Search All
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Data Sources
        </div>
    </div>


    <div class="menu-group">
        <div class="menu-group-box !flex-col justify-start">
            <div class="flex align-center my-1 justify-start">
                <ToggleSwitch inputId="sw-embedding"
                    class="mr-1"
                    v-model="store.features.embedding_search.enabled" />
                <label for="sw-embedding"
                    v-tooltip.bottom="'Embedding-based similarity search.'">
                    Embedding Search
                </label>
            </div>
            <div class="flex align-center my-1 justify-start">
                <ToggleSwitch inputId="sw-query-expansion"
                    class="mr-1"
                    v-model="store.features.query_expansion.enabled" />
                <label for="sw-query-expansion"
                    v-tooltip.bottom="'Use expanded query in search.'">
                    Query Expansion
                </label>
            </div>
        </div>
        <div class="menu-group-title">
            Search Options
        </div>
    </div>


    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Save the current mapping to the server and close mapping.'"
                @click="onClickSaveClose">
                <i class="fa-regular fa-floppy-disk menu-icon"></i>
                <span>
                    Save &amp; Close
                </span>
            </Button>

            <SplitButton text
                v-tooltip.bottom="'Download the current mapping to local disk.'"
                :model="downloadOptions"
                @click="onClickDownload">
                <div class="flex flex-col">
                    <i class="fa-solid fa-download menu-icon"></i>
                    <span>
                        Download
                    </span>
                </div>
            </SplitButton>
        </div>
        <div class="menu-group-title">
            Save
        </div>
    </div>


    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Save the current mapping to the server.'"
                @click="onClickRerank">
                <i class="fa-solid fa-arrow-up-wide-short menu-icon"></i>
                <span>
                    Re-rank
                </span>
            </Button>

            <Button text
                class="menu-button"
                v-tooltip.bottom="'Download the current mapping to local disk.'"
                @click="onClickValueLinking">
                <i class="fa-solid fa-link menu-icon"></i>
                <span>
                    Value Linking
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            AI Tools
        </div>
    </div>

    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Show the user manual in a new window.'"
                @click="store.showGuide()">
                <i class="fa-solid fa-book menu-icon"></i>
                <span>
                    How-to Guide
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Help
        </div>
    </div>

</div>

<!-- main -->
<div class="main flex-row">

<!-- concept list -->
<Panel class="h-full term-list mr-2">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa fa-list "></i>
                        Concept List
                    </div>
                    <div class="panel-subtitle text-sm">
                        <b>{{ store.working_file_concepts.length }}</b>
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
                    class="term-filter"/>
                <Divider layout="vertical" class="!mx-2" />
                <Select v-model="store.mapping.sort_terms_by" 
                    :options="sort_term_options" 
                    optionLabel="name" 
                    placeholder="Sort by" 
                    class="term-sort"/>

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
                                <Tag :value="item.id" severity="success" />
                            </template>
                            <template v-else-if="store.hasSearchResults(item)">
                                <Tag :value="item.id" severity="info" />
                            </template>
                            <template v-else>
                                <Tag :value="item.id" severity="contrast" />
                            </template>
                        </div>
                        <div>
                            {{ item.term }}
                        </div>
                    </div>
                    <div class="term-concept">
                        <div class="flex flex-col text-small">
                            <div class="flex items-center">
                                <template v-if="store.hasSelectedResults(item)">
                                    <i class="fa-solid fa-arrow-right-to-bracket mr-1"></i>
                                    {{ store.getSelectedResults(item).length }} selected
                                </template>
                                <template v-else>
                                    <i class="fa fa-exclamation-triangle mr-1"></i>
                                    No concept selected
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
                        Description:
                        {{ item.description }}
                    </div>

                    <div class="term-additional">
                        <Accordion value="1" class="w-full px-2" :unstyled="true">
                            <AccordionPanel value="0">
                                <AccordionHeader>
                                    <i class="fa fa-info-circle mr-1"></i>
                                    Additional Information
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
            
                        <!-- <div class="w-full text-right pr-2">
                            <Button severity="secondary"
                                v-tooltip.right="'Show additional information for this concept.'"
                                class="btn-mini"
                                @click="onClickShowAdditionalInfo">
                                <i class="fa fa-info-circle"></i>
                                Additional Info
                            </Button>
                        </div> -->
                        <div class="term-additional-info">

                        </div>
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
                            <!-- <template v-else>
                                No results found
                            </template> -->
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
                        :options="sort_term_options" 
                        optionLabel="name" 
                        placeholder="Sort by" 
                        class="term-sort"/>
                    <Divider layout="vertical" class="!mx-2" />
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
                        :item_idx="item_idx" />
                </template>

            </div>
            <Divider />
            </template>

            <!-- result list -->
            <div class="text-lg font-bold mt-4">
                <i class="fa-solid fa-list-ul"></i>
                Search Results
                <!-- ({{ store.working_mappings[store.working_concept?.concept_id]?.search_results.length }}) -->
            </div>
            <template v-for="item, item_idx in store.working_mappings_search_results_without_selected">
                <SearchResultItem :item="item" 
                    :flag_selected="false"
                    :flag_enabled_value_mapping="false"
                    :item_idx="item_idx" />
            </template>
                
        </div>
    </Panel>
</div>

</div>

<!-- dialog for search all progress -->
<Dialog v-model:visible="prograss_visible" 
    modal 
    header="Progress of searching all concepts" 
    :style="{ width: '400px' }" 
    :closable="false">
    <p class="text-lg">
        Searched: 
        {{ prograss_value }} / {{ store.working_file_concepts.length }}
        ({{ (prograss_value / store.working_file_concepts.length * 100).toFixed(2) }}%)
    </p>
    <ProgressBar :value="prograss_value" mode="indeterminate"></ProgressBar>
</Dialog>

</template>

<style scoped>
.select-sources {
    width: 10rem;
}

.term-list {
    width: 460px;
    min-width: 460px;
    height: 100%;
}

.result-list {
    width: calc(100% - 460px);
}

.term-filter {
    width: 120px;
}
.term-sort {
    width: 120px;
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