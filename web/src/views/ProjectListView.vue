<script setup>
import { useDataStore } from '../DataStore';
import Papa from 'papaparse'
import { onMounted, ref } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { Jimin } from '../Jimin';
import * as toolbox from '../toolbox';

const store = useDataStore();
const visible_dialog_upload_file = ref(false);

function getSelectionOptions(file) {
    return file.columns.map((col) => {
        return {
            label: '[' + col + ']',
            code: col
        };
    });
}

function anyDuplicateColumns(file, column) {
    // TODO: optimize this function
    if (file[column] == '' || file[column] == null) return null;

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
    visible_dialog_upload_file.value = true;
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
    store.current_project = project;

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
    store.working_project = store.current_project;

    // set working file to this file
    store.working_file = file;

    // set working concepts
    try {
        let ret = await Jimin.getConceptsByFile(file.file_id);
        console.log('* got concepts:', ret);
        store.working_file_concepts = ret;

    } catch (err) {
        console.error(err);
        store.msg(err.message, 'Error', 'error');
        return;
    }

    // then, switch to the mapping view
    store.changeView('mapping');
}

async function onClickDownload(file) {
    console.log('* clicked Download');
}

async function onClickDeleteFile(file) {
    console.log('* clicked Delete File');

    // ask for confirmation
    if (!confirm('Are you sure to delete this file?')) {
        return;
    }

    // delete this file
    let ret = await Jimin.deleteFile(file.file_id);

    store.msg(ret.message);

    // update file list
    onClickProjectItem(store.current_project);
}

async function onClickDeleteProject(project) {
    console.log('* clicked Delete Project', project);

    // delete this project
    let ret = await Jimin.deleteProject(project.project_id);
    console.log('* deleted project:', ret);

    store.msg(ret.message);

    // update project list
    onClickUpdateProjectList();
}

///////////////////////////////////////////////////////////
// Create project
///////////////////////////////////////////////////////////
const new_project = ref({
    name: '',
    description: '',
})
const visible_dialog_create_project = ref();

async function onClickCreate() {
    console.log('* clicked Create Project', new_project.value);

    // send this project to backend
    let project = await Jimin.createProject(new_project.value);    
    console.log('* created project:', project);

    store.msg('Created a new project: ' + project.name);

    // update project list
    onClickUpdateProjectList();

    // close the dialog
    visible_dialog_create_project.value = false;
}

///////////////////////////////////////////////////////////
// Upload file
///////////////////////////////////////////////////////////
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
            Jimin.uploadFile(csv).then((data) => {
                console.log('* uploaded file:', data);
                store.msg(data.message);

                // update file list
                onClickProjectItem(store.current_project);

                // close the dialog
                visible_dialog_upload_file.value = false;
            });

            
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
                @click="visible_dialog_create_project = true">
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
                        <span v-if="store.projects.length > 0">
                            ({{ store.projects.length }})
                        </span>
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
            <div class="w-full project-item flex flex-row justify-between py-2 items-center">
                <div class="flex flex-row grow cursor-pointer"
                    @click="onClickProjectItem(project)">
                    <div class="project-name">
                        <i class="fa-solid fa-suitcase mr-2"></i>
                        <span v-if="project.project_id == store.current_project?.project_id"
                            class="font-bold">
                            {{ project.name }}
                        </span>
                        <span v-else>
                            {{ project.name }}
                        </span>
                    </div>
                </div>
                <div>
                    <Button 
                        severity="secondary"
                        size="small"
                        v-tooltip.bottom="'Delete this project.'"
                        @click="onClickDeleteProject(project)">
                        <i class="fa-solid fa-trash"></i>
                    </Button>
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
                        Project Files

                        <span v-if="store.files.length > 0">
                            ({{ store.files.length }})
                        </span>
                    </div>
                    <div class="panel-subtitle text-sm">
                    </div>
                </div>
            </div>
            <div>

            </div>
        </div>
    </template>

    <div class="flex flex-col h-full pr-2" 
        :style="{ height: 'calc(100vh - 18rem)'}"
        style="width: calc(100% + 1rem); overflow-y: auto;">
        <template v-for="file in store.files">
            <div class="w-full file-item flex flex-col py-2">
                <div class="file-name flex flex-row justify-between">
                    <div class="text-lg font-bold">
                        <i class="fa fa-file"></i>
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
                            <span v-if="anyDuplicateColumns(file, 'term') != null" 
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
                            <span v-if="anyDuplicateColumns(file, 'description') != null" 
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
                            <span v-if="anyDuplicateColumns(file, 'value') != null" 
                                class="text-xs text-red-500">
                                Duplicate columns
                            </span>
                        </div>
                    </div>
                </div>

                <div class="file-name flex flex-row justify-start">
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
                        @click="onClickDownload(file)">
                        <i class="fa-solid fa-download"></i>
                        Download
                    </Button>

                    <Button 
                        severity="danger"
                        size="small"
                        v-tooltip.bottom="'Delete this file.'"
                        @click="onClickDeleteFile(file)">
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
<Dialog v-model:visible="visible_dialog_upload_file" 
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



<!-- Dialog for create a new project -->
<Dialog v-model:visible="visible_dialog_create_project" 
    modal 
    header="Create a new project" 
    :style="{ width: '35rem' }">
    <span class="text-surface-500 dark:text-surface-400 block mb-8">
        Create a new project with the following information.
    </span>
    <div class="flex flex-col justify-start gap-4 mb-4">
        <div>
            <label for="name" class="font-semibold w-24">
                Project Name
            </label>
            <InputText v-model="new_project.name" 
                placeholder="Enter a project name" 
                class="w-full" />
        </div>
        
        <div>
            <label for="name" class="font-semibold w-24">
                Project Description (optional)
            </label>
            <InputText v-model="new_project.description" 
                placeholder="Enter a project description" 
                class="w-full" />
        </div>
    </div>
    <div class="flex justify-end gap-2">
        <Button label="Create" @click="onClickCreate" severity="secondary" />
    </div>
</Dialog>

</template>

<style scoped>
.project-list {
    width: 500px;
    margin: 0 0.5rem 0 0;
}
.project-detail {
    width: calc(100% - 400px);
}

.project-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--bd-color);
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