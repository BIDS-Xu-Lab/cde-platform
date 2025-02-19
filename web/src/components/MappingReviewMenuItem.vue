<script setup>
import ToggleSwitch from 'primevue/toggleswitch';
import Papa from 'papaparse'
import { stringify } from 'yaml'
import { useDataStore } from '../DataStore';
import { ref } from 'vue';
import { Button } from 'primevue';

import * as CDEHelper from '../CDEHelper';
import { Jimin } from '../Jimin';
const props = defineProps({
    view_mode: String
});

const store = useDataStore();
const prograss_visible = ref(false);
const submit_dialog_visible = ref(false);
const prograss_value = ref(0);

async function onClickSubmitButton() {
    console.log('* clicked Submit Button');
    submit_dialog_visible.value = true;
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
        // get the current stored selected_results
        const selectedResults = store.working_mappings[store.working_concept.concept_id].selected_results;

        // remove duplicates based on term_id + term_source as unique key
        const uniqueResults = Array.from(
            new Map(results[0].map(item => [`${item.term_id}-${item.term_source}`, item])).values()
        );

        // filter out the items that are already in selected_results
        store.working_mappings[store.working_concept.concept_id].search_results = uniqueResults.filter(
            item => !selectedResults.some(sel => sel.term_id === item.term_id && sel.term_source === item.term_source)
        );
    } else {
        store.working_mappings[store.working_concept.concept_id] = {
            search_results: results[0],
            selected_results: [],
            reviewed_results: [],
            mapper_suggestion: false,
            reviewer_suggestion: false,
            status: 'mapping'
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
        // skip final concepts
        if(concept.final){
            continue;
        }
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
            // get the current stored selected_results
            const selectedResults = store.working_mappings[concept.concept_id].selected_results;

            // remove duplicates based on term_id + term_source as unique key
            const uniqueResults = Array.from(
                new Map(results[0].map(item => [`${item.term_id}-${item.term_source}`, item])).values()
            );

            // filter out the items that are already in selected_results
            store.working_mappings[concept.concept_id].search_results = uniqueResults.filter(
                item => !selectedResults.some(sel => sel.term_id === item.term_id && sel.term_source === item.term_source)
            );
        } else {
            store.working_mappings[concept.concept_id] = {
                search_results: results[0],
                selected_results: [],
                reviewed_results: [],
                mapper_suggestion: false,
                reviewer_suggestion: false,
                status: 'mapping'
            }
        }
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    // sleep 1 sec let animation can be shown
    
    prograss_visible.value = false;
    prograss_value.value = 0;
    store.msg('Searched all results.');
}

async function onClickSaveWork() {
    console.log('* clicked Save and Close');

    // send request to backend
    let ret = await Jimin.saveFile(store.working_file.file_id);

    // download the result to local disk
    let blob = new Blob([JSON.stringify(ret, false, 2)], { type: 'application/json' });
    let url = URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    // remove extension
    a.download = store.working_file.filename.replace(/\.[^/.]+$/, "") + '.json';
    a.click();


    // save the current mappings to the server
    // just sleep 3 seconds
    store.msg('Saved the current file.');
}

async function onClickDownload() {
    console.log('* clicked Download');
    let ret = await Jimin.saveFile(store.working_file.file_id);
    // convert ret to JSONL file
    //first loop through the ret.concepts
    let concepts_result = [];
    for (let i = 0; i < ret.concepts.length; i++) {
        let concept = ret.concepts[i];

        for (let j = 0; j < ret.mappings.length; j++) {
            let mapping = ret.mappings[j];
            if (mapping.concept_id == concept.id) {
                concept['mapping'] = mapping;
                break;
            }
        }
        concepts_result.push(concept);
    }
    // convert concepts to JSONL
    let blob = new Blob([concepts_result.map(x => JSON.stringify(x)).join('\n')], { type: 'application/json' });
    let url = URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    // remove extension, let extension be jsonl
    a.download = store.working_file.filename.replace(/\.[^/.]+$/, "") + '.jsonl';
    a.click();
}

async function onClickSubmitWork() {
    console.log('* clicked Submit Work');
    // close the dialog
    submit_dialog_visible.value = false;
    // send the current mappings to the server
    let ret = await Jimin.submitMappingWork(store.working_file.file_id);
    
    //unbound the working file
    store.working_file = null;
    store.working_file_concepts = [];
    store.working_concept = null;
    store.working_mappings = {};
    // redirect to the project view
    await store.updateCurrentProjectFiles();
    store.changeView('project_list');
    if (ret.success) {
        store.msg(ret.message);
    } else {
        store.msg(ret.message, 'error', 'error');
    }
}

async function onClickDownloadYAML() {
    console.log('* clicked Download YAML');
    let ret = await Jimin.saveFile(store.working_file.file_id);
    // convert ret to YAML file
    //first loop through the ret.concepts
    let concepts_result = [];
    for (let i = 0; i < ret.concepts.length; i++) {
        let concept = ret.concepts[i];

        for (let j = 0; j < ret.mappings.length; j++) {
            let mapping = ret.mappings[j];
            if (mapping.concept_id == concept.id) {
                concept['mapping'] = mapping;
                break;
            }
        }
        concepts_result.push(concept);
    }
    // convert concepts to YAML
    let blob = new Blob([stringify(concepts_result)], { type: 'application/json' });
    let url = URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    // remove extension, let extension be yaml
    a.download = store.working_file.filename.replace(/\.[^/.]+$/, "") + '.yaml';
    a.click();
}

async function onClickDownloadTSV() {
    console.log('* clicked Download');
    let ret = await Jimin.saveFile(store.working_file.file_id);
    // convert ret to JSONL file
    //first loop through the ret.concepts
    let concepts_result = [];
    for (let i = 0; i < ret.concepts.length; i++) {
        let concept = ret.concepts[i];

        for (let j = 0; j < ret.mappings.length; j++) {
            let mapping = ret.mappings[j];
            if (mapping.concept_id == concept.id) {
                // convert mapping JSON to string
                concept['mapping'] = JSON.stringify(mapping);
                
                break;
            }
        }
        concepts_result.push(concept);
    }
    // use papaparse to convert concepts to TSV
    let blob = new Blob([Papa.unparse(concepts_result,{delimiter:'\t'})], { type: 'text/tsv' });
    let url = URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    // remove extension, let extension be jsonl
    a.download = store.working_file.filename.replace(/\.[^/.]+$/, "") + '.tsv';
    a.click();
}
const downloadOptions = [{
    icon: 'pi pi-file',
    label: 'JSONL Format',

    command: () => {
        onClickDownload();
        store.toast.add({ severity: 'success', summary: 'Downloaded successfully!', detail: 'Downloaded all data into a single JSONL file.', life: 3000 });
    }
},
{
    icon: 'pi pi-file',
    label: 'YAML Format',
    command: () => {
        onClickDownloadYAML();
        store.toast.add({ severity: 'success', summary: 'Downloaded successfully!', detail: 'Downloaded all data into a single YAML file.', life: 3000 });
    }
},
{
    icon: 'pi pi-file-excel',
    label: 'TSV Format',
    title: "Download all data into a single TSV file.",
    command: () => {
        onClickDownloadTSV();
        store.toast.add({ severity: 'success', summary: 'Downloaded successfully!', detail: 'Downloaded all data into a single TSV file.', life: 3000 });
    }
},
{
    separator: true
},
{
    label: 'Raw JSON Format',
    command: () => {
        onClickSaveWork();
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


</script>

<template>
<div class="menu">
    <div  v-if="view_mode!=='finalized'" class="menu-group !ml-2">
        <div class="menu-group-box">
            <Button text
                :disabled="CDEHelper.checkSubmitAndFinalStatus()"
                class="menu-button"
                v-tooltip.bottom="'Refresh list.'"
                @click="CDEHelper.onClickRefreshListGetSources">
                <font-awesome-icon icon="fa-solid fa-rotate" class="menu-icon" />
                <span>
                    Refresh
                </span>
            </Button>

            <div class="flex flex-col mr-2">
                <label class="text-sm">
                    <font-awesome-icon icon="fa-solid fa-database"></font-awesome-icon>
                    Sources
                </label>
                <Select v-model="store.mapping.selected_source"
                    :disabled="CDEHelper.checkSubmitAndFinalStatus()"
                    :options="store.mapping.sources" 
                    @change="onChangeSource"
                    variant="in"
                    filter 
                    optionLabel="name" 
                    optionValue="code" 
                    placeholder="Select a data source" 
                    v-tooltip.bottom="'Select a data source to search.'"
                    class="select-sources">
                    <template #header>
                        <div class="font-bold px-3">Available Sources</div>
                    </template>
                </Select>
            </div>

            <div class="flex flex-col">
                <label class="text-sm" for="">
                    <font-awesome-icon icon="fa-solid fa-book-bookmark"></font-awesome-icon>
                    Collections
                </label>
                <MultiSelect v-model="store.mapping.selected_collections" 
                    :disabled="CDEHelper.checkSubmitAndFinalStatus()"
                    :options="store.mapping.collections" 
                    variant="in"
                    filter 
                    optionLabel="name" 
                    optionValue="code" 
                    placeholder="Select data collections" 
                    v-tooltip.bottom="'Filter data collections to search.'"
                    class="select-sources">
                    <template #header>
                        <div class="font-bold px-3">Available Collections</div>
                    </template>
                </MultiSelect>
            </div>

            <Button text
                :disabled="CDEHelper.checkSubmitAndFinalStatus()"
                class="menu-button"
                v-tooltip.bottom="'Search CDEs for the current selected concept.'"
                @click="onClickSearch">
                <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="menu-icon" />
                <span>
                    Search
                </span>
            </Button>
            <Button text
                :disabled="CDEHelper.checkSubmitAndFinalStatus()"
                class="menu-button"
                v-tooltip.bottom="'Search CDEs for all terms.'"
                @click="onClickSearchAll">
                <font-awesome-icon icon="fa-brands fa-searchengin" class="menu-icon" />
                <span>
                    Search All
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Data Sources
        </div>
    </div>


    <div v-if="view_mode!=='finalized'" class="menu-group">
        <div class="menu-group-box !flex-col justify-start">
            <div class="flex align-center my-1 justify-start">
                <ToggleSwitch inputId="sw-embedding"
                    :disabled="CDEHelper.checkSubmitAndFinalStatus()"
                    class="mr-1"
                    v-model="store.features.embedding_search.enabled" />
                <label for="sw-embedding"
                    v-tooltip.bottom="'Embedding-based similarity search.'">
                    Embedding Search
                </label>
            </div>
            <div class="flex align-center my-1 justify-start">
                <ToggleSwitch inputId="sw-query-expansion"
                    :disabled="CDEHelper.checkSubmitAndFinalStatus()"
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
                v-if="view_mode!=='finalized'"
                :disabled="Object.values(store.working_mappings).some(mapping => mapping.status === 'mapped' || mapping.status === 'reviewed')"
                class="menu-button"
                v-tooltip.bottom="'Save the current mapping results as a JSON file to local disk.'"
                @click="onClickSubmitButton">
                <font-awesome-icon icon="fa-solid fa-upload" class="menu-icon" />
                <span>
                    Submit
                </span>
            </Button>

            <SplitButton text
                v-tooltip.bottom="'Export the current mapping results as a JSONL format file to local disk.'"
                :model="downloadOptions"
                @click="onClickDownload">
                <div class="flex flex-col">
                    <font-awesome-icon icon="fa-solid fa-download" class="menu-icon mb-2" />
                    <span>
                        Export
                    </span>
                </div>
            </SplitButton>
        </div>
        <div class="menu-group-title">
            Save
        </div>
    </div>


    <div v-if="view_mode!=='finalized'" class="menu-group">
        <div class="menu-group-box">
            <Button text
                :disabled="CDEHelper.checkSubmitAndFinalStatus()"
                class="menu-button"
                v-tooltip.bottom="'Re-rank the current search results using AI technology.'"
                @click="onClickRerank">
                <font-awesome-icon icon="fa-solid fa-arrow-up-wide-short" class="menu-icon" />
                <span>
                    Re-rank
                </span>
            </Button>

            <Button text
                :disabled="CDEHelper.checkSubmitAndFinalStatus()"
                class="menu-button"
                v-tooltip.bottom="'Automatically link the values to the current CDE\'s values.'"
                @click="onClickValueLinking">
                <font-awesome-icon icon="fa-solid fa-link" class="menu-icon" />
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
                <font-awesome-icon icon="fa-solid fa-book" class="menu-icon" />
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

<!-- dialog for submit -->
<Dialog v-model:visible="submit_dialog_visible" 
    modal 
    header="Do you want to submit the current work?" 
    :style="{ width: '400px' }" 
    :closable="false">
    <p class="text-lg">
        If you submit the current work, you cannot modify it anymore.
    </p>
    <div class="flex justify-end">
        <Button label="Cancel" class="mr-2" @click="submit_dialog_visible = false" />
        <Button label="Submit" class="p-button-success" @click="onClickSubmitWork" />
    </div>
</Dialog>
</template>
<style scoped>
.select-sources {
    width: 10rem;
}
</style>