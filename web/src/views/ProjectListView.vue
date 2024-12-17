<script setup>
import { useDataStore } from '../DataStore';
import Papa from 'papaparse'
import { onMounted, ref } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { Jimin } from '../Jimin';
import * as toolbox from '../toolbox';

const store = useDataStore();
const visible = ref(false);

function getSelectionOptions(file) {
    return file.columns.map((col) => {
        return {
            label: '[' + col + ']',
            code: col
        };
    });
}

function hasDuplicateColumns(file, column) {
    // TODO: optimize this function
    if (file[column] == '') return null;

    if (column == 'term') {
        if (file.description == file.term) {
            return 'description';
        }
        if (file.value == file.term) {
            return 'value';
        }
        return null;
    }

    if (column == 'description') {
        if (file.term == file.description) {
            return 'term';
        }
        if (file.value == file.description) {
            return 'value';
        }
        return null;
    }

    if (column == 'value') {
        if (file.term == file.value) {
            return 'term';
        }
        if (file.description == file.value) {
            return 'description';
        }
        return null;
    }
}

function onClickSave() {
    console.log('* clicked Save');
}

function onClickNewFile() {
    console.log('* clicked New File');
    visible.value = true;
}

async function onClickUpdateProjectList() {
    console.log('* clicked Update Project List');

    // get all projects
    let projects = await Jimin.getProjects();

    // update store
    store.projects = projects;
}

async function onClickProjectItem(project) {
    console.log('* clicked Project Item', project);
    store.currentProject = project;

    // get all files for this project
    let files = await Jimin.getFilesByProject(project.project_id);
    console.log('* got project files:', files);

    store.files = files;
}

async function onClickMapping(file) {
    console.log('* clicked Mapping');

    // first, update the selected columns
    let ret = await Jimin.updateFile(file);
    console.log('* updated file:', ret);

    store.msg(ret.message);

    // set working project to this project
    store.working_project = store.currentProject;

    // set working file to this file
    store.working_file = file;

    // then, switch to the mapping view
    store.changeView('mapping');
}

async function onClickDownload() {
    console.log('* clicked Download');
}

async function onClickDeleteFile() {
    console.log('* clicked Delete File');
}

const fileupload = ref();
store.fileupload = fileupload;
const selected_project_for_file = ref();

const onClickUpload = () => {
    // fileupload.value.upload();
    let file = fileupload.value.files[0];
    Papa.parse(file, {
        complete: (result) => {
            // Create an object representing the file to add to the store
            const csv = {
                filename: file.name,
                concepts: result.data,
                created: toolbox.formatDate(new Date()),
                updated: toolbox.formatDate(new Date()),
                // Add any additional properties you need
            };
            csv['project_id'] = selected_project_for_file.value | '';
            csv["columns"] = Object.keys(csv.concepts[0]);
            csv["file_id"] = uuidv4();
            csv['user_id'] = store.user.user_id | 0;
            csv["currentConceptId"] = 0;
            csv["updated"] = toolbox.formatDate(new Date());
            csv["concepts"] = csv.concepts.map((concept, index) => {
                return {
                    ...concept,
                    // user_id: this.userId,
                    file_id: csv["file_id"],
                    id: index,
                };
            });
            // Empty preselected items
            csv["term"] = '';
            csv["description"] = '';
            csv["value"] = '';

            console.log('* generated csv:', csv);

            // send this csv to backend
            Jimin.uploadFile(csv);
        },
        header: true, // Set to true if your CSV has a header row
        skipEmptyLines: true,
    });
};

onMounted(() => {
    console.log('* mounted ProjectListView');
    onClickUpdateProjectList();
});

</script>

<template>
<div class="menu">
    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.right="'Create a new project.'"
                @click="onClickSave">
                <i class="fa-regular fa-save menu-icon"></i>
                <span>
                    New Project
                </span>
            </Button>

            <Button text
                class="menu-button"
                v-tooltip.bottom="'Update project list.'"
                @click="onClickUpdateProjectList">
                <i class="fa-solid fa-rotate menu-icon"></i>
                <span>
                    Update List
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Project
        </div>
    </div>


    <div class="menu-group">
        <div class="menu-group-box">

            <Button text
                class="menu-button"
                v-tooltip.bottom="'Import a new data file.'"
                @click="onClickNewFile">
                <i class="fa-regular fa-file menu-icon"></i>
                <span>
                    Add File
                </span>
            </Button>

            <Button text
                class="menu-button"
                v-tooltip.bottom="'Update project list.'"
                @click="onClickSave">
                <i class="fa-solid fa-rotate menu-icon"></i>
                <span>
                    Update List
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            File
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


<div class="main">

<Panel class="h-full project-list">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa-solid fa-list"></i>
                        All Projects
                    </div>
                    <div class="panel-subtitle text-sm">
                    </div>
                </div>
            </div>
            <div>

            </div>
        </div>
    </template>

    <div>
        <template v-for="project in store.projects">
            <div class="w-full project-item"
                @click="onClickProjectItem(project)">
                <div class="project-name">
                    {{ project.name }}
                </div>
            </div>
        </template>
    </div>
</Panel>


<Panel class="h-full project-detail">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa-solid fa-briefcase"></i>
                        Project Detail
                    </div>
                    <div class="panel-subtitle text-sm">
                    </div>
                </div>
            </div>
            <div>

            </div>
        </div>
    </template>

    <div>
        <template v-for="file in store.files">
            <div class="w-full file-item flex flex-col py-2">
                <div class="file-name flex flex-row justify-between">
                    <div class="text-lg font-bold">
                        {{ file.filename }}
                    </div>
                    <div class="file-reviewers mt-2 py-2">
                    Assigned Reviewers: 
                    <i class="fa fa-user"></i>
                </div>
                </div>
                <div class="file-column flex flex-row mb-2">
                    <div class="flex flex-col mr-2 w-col-select-box">
                        <label for="">Term</label>
                        <Select v-model="file.term" 
                            :options="getSelectionOptions(file)"
                            optionLabel="label" 
                            optionValue="code"
                            placeholder="Select a term column" 
                            class="w-full" />
                        <div>
                            <span v-if="hasDuplicateColumns(file, 'term')" 
                                class="text-xs text-red-500">
                                Duplicate columns
                            </span>
                        </div>
                    </div>

                    <div class="flex flex-col w-col-select-box mr-2">
                        <label for="">Description</label>
                        <Select v-model="file.description" 
                            :options="getSelectionOptions(file)"
                            optionLabel="label" 
                            optionValue="code"
                            placeholder="Select a description column" 
                            class="w-full" />
                        <div>
                            <span v-if="hasDuplicateColumns(file, 'description')" 
                                class="text-xs text-red-500">
                                Duplicate columns
                            </span>
                        </div>
                    </div>

                    <div class="flex flex-col w-col-select-box">
                        <label for="">Value</label>
                        <Select v-model="file.value" 
                            :options="getSelectionOptions(file)"
                            optionLabel="label" 
                            optionValue="code"
                            placeholder="Select a value column" 
                            class="w-full" />
                        <div>
                            <span v-if="hasDuplicateColumns(file, 'value')" 
                                class="text-xs text-red-500">
                                Duplicate columns
                            </span>
                        </div>
                    </div>
                </div>
                <div class="file-name flex flex-row justify-end">
                    <Button 
                        severity="secondary"
                        size="small"
                        class="mr-2"
                        v-tooltip.bottom="'Mapping concepts for this file.'"
                        @click="onClickMapping(file)">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        Mapping
                    </Button>

                    <Button 
                        severity="info"
                        size="small"
                        class="mr-2"
                        v-tooltip.bottom="'Download this file.'"
                        @click="onClickDownload">
                        <i class="fa-solid fa-download"></i>
                        Download
                    </Button>

                    <Button 
                        severity="danger"
                        size="small"
                        v-tooltip.bottom="'Delete this file.'"
                        @click="onClickDeleteFile">
                        <i class="fa-solid fa-trash"></i>
                        Delete
                    </Button>
                </div>

            </div>
        </template>
    </div>
</Panel>


</div>

<!-- Dialog for uploading a new file -->
<Dialog v-model:visible="visible" 
    modal 
    header="Upload file" 
    :style="{ width: '25rem' }">
    <span class="text-surface-500 dark:text-surface-400 block mb-8">
        Upload your .csv file for the following project.
    </span>
    <div class="flex flex-col justify-start gap-4 mb-4">
        <div>
            <label for="select_project" class="font-semibold w-24">
                Select a Project
            </label>
            <Select v-model="selected_project_for_file" 
                :options="store.projects"
                optionLabel="name" 
                optionValue="project_id"
                placeholder="Select a project" 
                class="w-full" />
        </div>
        <label for="select_file" class="font-semibold w-24">Select File</label>
        <FileUpload ref="fileupload" 
            mode="basic" name="demo[]" 
            url="/api/upload" 
            accept="text/csv" />
    </div>
    <div class="flex justify-end gap-2">
        <Button label="Upload" @click="onClickUpload" severity="secondary" />
    </div>
</Dialog>

</template>

<style scoped>
.project-list {
    width: 400px;
    margin: 0 0.5rem 0 0;
}
.project-detail {
    width: calc(100% - 400px);
}

.project-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--bd-color);
    cursor: pointer;
}
.project-item:hover {
    background-color: var(--bg-color-menu-hover);
}

.file-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--bd-color);
}

.file-item:hover {
    background-color: var(--bg-color-menu-hover);
}

.w-col-select-box {
    width: 180px !important;
}
</style>