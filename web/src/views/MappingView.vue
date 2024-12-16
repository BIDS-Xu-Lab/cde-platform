<script setup>
import ToggleSwitch from 'primevue/toggleswitch';
import VirtualScroller from 'primevue/virtualscroller';
import Badge from 'primevue/badge';

import { useDataStore } from '../DataStore';
import { onMounted, ref } from 'vue';
import { Button } from 'primevue';

import * as CDEHelper from '../CDEHelper';
import Footer from '../components/Footer.vue';

const store = useDataStore();

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
    console.log('Clicked term:', item);
}

onMounted(() => {
    console.log('MappingView mounted');
});
</script>

<template>
<div class="menu">
    <div class="menu-group !ml-2">
        <div class="menu-group-box">
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


<div class="main flex-row">
<!-- term list -->
<div class="term-list">
    <Panel class="h-full">
        <template #header>
            <div class="w-full flex justify-between">
                <div class="flex">
                    <div class="flex-col">
                        <div class="text-lg font-bold">
                            <i class="fa fa-list "></i>
                            Term List
                        </div>
                        <div class="panel-subtitle text-sm">
                            <b>{{ store.file.length }}</b>
                            /
                            {{ store.file.length }}  
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
            <VirtualScroller :items="store.file" 
                class="term-list-scroller"
                :style="{ height: 'calc(100vh - 18rem)'}"
                :itemSize="50">
                <template v-slot:item="{ item, options }">
                    <div class="term-line"
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
                            <div>
                                <span v-if="CDEHelper.hasSelectedResult(item)">
                                    {{ CDEHelper.getSelectedResult(item)?.standardConcept }}
                                </span>
                                <span v-else>
                                    <i class="fa fa-exclamation-triangle"></i>
                                    No concept selected
                                </span>
                            </div>
                            <div>
                                <Button
                                    size="small"
                                    icon="pi pi-times"
                                    label="De-select"
                                    class="mr-1"
                                    v-tooltip.right="'De-select this concept.'"
                                    @click="store.showGuide()">
                                </Button>
                            </div>
                        </div>
                    </div>
                </template>
            </VirtualScroller>

        </div>
    </Panel>
</div>

<!-- result list -->
<div class="result-list">
    <Panel class="h-full">
        <template #header>
            <div class="w-full flex justify-between">
                <div class="flex">
                    <div class="flex-col">
                        <div class="text-lg font-bold">
                            <i class="fa-solid fa-cubes"></i>
                            CDE Mapping
                        </div>
                        <div class="panel-subtitle text-sm">
                            CDEs
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
    </Panel>
</div>

</div>

<Footer />

</template>

<style scoped>
.select-sources {
    width: 15rem;
}

.term-list {
    width: 460px;
    min-width: 360px;
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
    width: 100%;
}
.term-line {
    width: 100%;
    border-bottom: 1px solid var(--bd-color);
    padding: 0.5rem 0;
    margin: 0.5rem 0;
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
    font-size: 1.2rem;
}
.term-concept {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
}
</style>