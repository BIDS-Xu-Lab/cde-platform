<script setup>
import ToggleSwitch from 'primevue/toggleswitch';
import VirtualScroller from 'primevue/virtualscroller';
import Badge from 'primevue/badge';

import { useDataStore } from '../DataStore';
import { onMounted, ref } from 'vue';
import { Button } from 'primevue';

import * as CDEHelper from '../CDEHelper';
import { Jimin } from '../Jimin';

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

    if (store.working_concept == null) {
        store.msg('Please select a concept to search.');
        return;
    }

    // search CDEs on the working concept
    let results = await Jimin.search(
        store.mapping.selected_source,
        store.mapping.selected_collections,
        [CDEHelper.convertConceptToQueryByFile(
            store.working_concept, 
            store.working_file
        )],
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

function onClickSearchAll() {
    console.log('* clicked Search All');
}

function onClickSave() {
    console.log('* clicked Save');
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

function onClickConcept(concept) {
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
                v-tooltip.bottom="'Save the current mapping to the server.'"
                @click="onClickSave">
                <i class="fa-regular fa-floppy-disk menu-icon"></i>
                <span>
                    Save
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
<Panel class="h-full term-list">
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
            <template v-for="item in store.working_file_concepts">
                <div class="term-line"
                    :class="{ 'working-term': store.isWorkingConcept(item) }"
                    @click="onClickConcept(item)">
                    <div class="term-name">
                        <div class="mr-1">
                            <template v-if="true">
                                <Badge :value="item.id" severity="success" />
                            </template>
                            <template v-else>
                                <Badge :value="item.id" severity="warning" />
                            </template>
                        </div>
                        <div>
                            {{ item[store.mapping.data_col_term] }}
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
                        {{ item[store.mapping.data_col_description] }}
                    </div>

                    <div class="term-additional">
                        <div class="w-full text-right pr-2">
                            <i class="fa fa-info-circle"></i>
                            Additional Info
                        </div>
                        <div class="term-additional-info">

                        </div>
                    </div>
                </div>
            </template>
        </div>

    </div>
</Panel>

<!-- result list -->
<Panel class="h-full result-list">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa-solid fa-cubes"></i>
                        CDE Mapping 
                        <b v-if="store.working_concept">
                            {{ store.working_concept?.[store.mapping.data_col_term] }}
                        </b>
                    </div>
                    <div class="panel-subtitle text-sm">
                        <template v-if="store.working_mappings[store.working_concept?.concept_id]?.search_results.length > 0">
                            <b>{{ store.working_mappings[store.working_concept?.concept_id]?.search_results.length }}</b>
                            potential matches found
                        </template>
                        <template v-else>
                            No results found
                        </template>
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
                <Divider layout="vertical" class="!mx-2" />
                <Select v-model="store.mapping.sort_order_by" 
                    :options="sort_order_options" 
                    optionLabel="name" 
                    placeholder="Order by" 
                    class="term-sort"/>

            </div>
        </div>
    </template>

    <div class="result-list-box">
        <div class="result-list-scroller"
            :style="{ height: 'calc(100vh - 18rem)'}">
            <template v-for="item, item_idx in store.working_mappings[store.working_concept?.concept_id]?.search_results">
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
                            <Button
                                size="small"
                                icon="pi pi-check"
                                severity="success"
                                label="Select"
                                class="mr-1"
                                v-tooltip.right="'Select this concept.'"
                                @click="onClickSelectResult(item)">
                            </Button>
                        </div>  
                    </div>

                    <div class="result-detail">
                        Question Text:
                        {{ item.description }}
                    </div>

                    <div class="result-valueset">
                        <div>
                            <Button
                                size="small"
                                icon="pi pi-list"
                                label="Value Mapping"
                                severity="secondary"
                                class="btn-mini"
                                v-tooltip.right="'Map values for this concept.'"
                                @click="store.showGuide()">
                            </Button>
                        </div>
                    </div>
                    
                </div>
            </template>
        </div>
    </div>
</Panel>

</div>


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
    height: 100%;
    margin: 0 0 0 0.5rem;
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


.result-list-box {
    height: 100%;
}
.result-list-scroller {
    width: calc(100% + 1rem);
    overflow-y: auto;
}
.result-line {
    width: 100%;
    border-bottom: 1px solid var(--bd-color);
    padding: 0.5rem 0;
    display: flex;
    flex-direction: column;
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