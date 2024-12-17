<script setup>
import ToggleSwitch from 'primevue/toggleswitch';
import VirtualScroller from 'primevue/virtualscroller';
import Badge from 'primevue/badge';

import { useDataStore } from '../DataStore';
import { onMounted, ref } from 'vue';
import { Button } from 'primevue';

import * as CDEHelper from '../CDEHelper';

const store = useDataStore();
function onClickRefreshList() {
    console.log('* clicked Refresh List');
}

function onClickSearch() {
    console.log('* clicked Search ');
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

function onClickTerm(item) {
    console.log('* clicked term:', item);

    store.working_term_idx = store.working_file_concepts.indexOf(item);
    console.log('* clicked working_term_idx:', store.working_term_idx);
}

function fmtScore(score) {
    return score.toFixed(2);
}

onMounted(() => {
    console.log('* mounted MappingView');
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
                <Select v-model="store.mapping.selected_sources" 
                    :options="store.mapping.sources" 
                    variant="in"
                    filter 
                    optionLabel="name" 
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
                <Select v-model="store.mapping.selected_sources" 
                    :options="store.mapping.sources" 
                    variant="in"
                    filter 
                    optionLabel="name" 
                    placeholder="Select a data source" 
                    class="select-sources">
                    <template #header>
                        <div class="font-bold px-3">Available Collections</div>
                    </template>
                </Select>
            </div>

            <Button text
                class="menu-button"
                v-tooltip.bottom="'Search CDEs for the current selected term.'"
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

<!-- term list -->
<Panel class="h-full term-list">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa fa-list "></i>
                        Term List
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
                    :class="{ 'working-term': store.isWorkingTerm(item) }"
                    @click="onClickTerm(item)">
                    <div class="term-name">
                        <div class="mr-1">
                            <template v-if="CDEHelper.hasSelectedResult(item)">
                                <Badge :value="item.id" severity="success" />
                            </template>
                            <template v-else>
                                <Badge :value="item.id" severity="warning" />
                            </template>
                        </div>
                        <div>
                            {{ item[store.mapping.data_col_name] }}
                        </div>
                    </div>
                    <div class="term-concept">
                        <div class="flex items-center text-small">
                            <template v-if="CDEHelper.hasSelectedResult(item)">
                                <i class="fa-solid fa-arrow-right-to-bracket mr-1"></i>
                                <span>
                                    {{ CDEHelper.getSelectedResult(item)?.conceptSource }} / 
                                    {{ CDEHelper.getSelectedResult(item)?.standardConcept }}
                                </span>
                            </template>
                            <template v-else>
                                <i class="fa fa-exclamation-triangle mr-1"></i>
                                No concept selected
                            </template>
                        </div>
                        <div>
                            <Button v-if="CDEHelper.hasSelectedResult(item)"
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
                        <b v-if="store.working_term">
                            {{ store.working_term?.[store.mapping.data_col_name] }}
                        </b>
                    </div>
                    <div class="panel-subtitle text-sm">
                        <template v-if="store.working_term?.results.length > 0">
                            <b>{{ store.working_term?.results.length }}</b>
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

            </div>
        </div>
    </template>

    <div class="result-list-box">
        <div class="result-list-scroller"
            :style="{ height: 'calc(100vh - 18rem)'}">
            <template v-for="item, item_idx in store.working_term?.results">
                <div class="result-line">
                    <div class="result-tags">
                        <div class="flex flex-row">
                            <div class="pr-3">
                                {{ item_idx + 1 }}
                            </div>
                            <Badge :value="fmtScore(item.score)" 
                                class="mr-1 badge-score"
                                severity="info" />
                            <Badge :value="item.conceptSource" severity="info" />
                        </div>

                        <div>

                        </div>
                    </div>
                    <div class="result-name">
                        <div class="flex items-center">
                            <div>
                                {{ item.standardConcept }}
                            </div>
                            <Divider layout="vertical" class="!mx-2" />
                            <div class="text-base">
                                <a :href="'https://cde.nlm.nih.gov/deView?tinyId=' + item.conceptId"
                                    target="_blank">
                                    <i class="fa fa-globe"></i>
                                    {{ item.conceptId }}
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
                                @click="store.showGuide()">
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
    align-items: center;
    font-size: 1.2rem;
}
.term-concept {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
}
.term-additional {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.working-term {
    background-color: var(--bg-color-menu-hover);
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