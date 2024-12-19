<script setup>
import { useDataStore } from '../DataStore';
import Papa from 'papaparse'
import { onMounted, ref } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { Jimin } from '../Jimin';
import * as toolbox from '../toolbox';
import { hasResults } from '../CDEHelper';

const store = useDataStore();
const visible_dialog_upload_file = ref(false);
// const visible_dialog_move_file = ref(false);
// const selected_project_for_move = ref();
// const selected_file_for_move = ref();

function anyDuplicateColumns(file, column) {
    // Return null if the column is empty
    if (!file[column]) return null;

    // Define the columns to check against
    const columnsToCheck = {
        term: ['description', 'value'],
        description: ['term', 'value'],
        value: ['term', 'description']
    };

    // Get the columns we need to compare with
    const comparisons = columnsToCheck[column];

    // Check if the current column value matches any other column
    for (const compareColumn of comparisons) {
        if (file[column] === file[compareColumn]) {
            return compareColumn;
        }
    }

    return null;
}

function onClickSave() {
    console.log('* clicked Save');
}

function onClickNewFile() {
    console.log('* clicked New File');
    visible_dialog_upload_file.value = true;
}

function onClickNewFileForProject(project) {
    console.log('* clicked New File for Project', project);
    selected_project_id_for_file.value = project.project_id;
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

    // if project is null or undefined, return
    if (!project) {
        return;
    }

    store.current_project = project;

    // get all files for this project
    let files = await Jimin.getFilesByProject(project.project_id);
    console.log('* got project files:', files);

    store.files = files;
}

async function onClickMapping(file) {
    console.log('* clicked Mapping');

    // clear the existing mapping data
    store.clearMappingData();

    // set working project to this project
    store.working_project = store.current_project;

    // set working file to this file
    store.working_file = file;

    // set working concepts
    try {
        let ret = await Jimin.getConceptsByFile(file.file_id);
        console.log('* got concepts:', ret);

        // set working concepts and mapping to default
        store.working_file_concepts = ret.concepts;
        store.working_mappings = {};

        // put all concepts into the working mappings
        ret.mappings.forEach((mapping) => {
            store.working_mappings[mapping.concept_id] = {
                selected_results: mapping.selected_results,
                search_results: mapping.search_results
            };
        });

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

// async function onClickMove() {
//     console.log('* clicked Move');
//     visible_dialog_move_file.value = true;
//     await Jimin.moveFile(selected_file_for_move.file_id, selected_project_for_move.project_id);
//     store.msg('Moved file to ' + project.name);
//     selected_file_for_move = null;
//     selected_project_for_move = null;
//     onClickProjectItem(project);
    
    
//     // move this file to selected project
// }
async function onClickDeleteFile(file) {
    console.log('* clicked Delete File');

    // ask for confirmation
    if (!confirm('Are you sure to delete this file?')) {
        return;
    }

    // delete this file
    let ret = await Jimin.deleteFile(file.file_id);
    // if this file is the working file, reset the working file
    if (file.file_id == store.working_file.file_id) {
        store.working_file = null;
        store.working_file_concepts = [];
        store.working_concept = null;
    }

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
// Reviewers
///////////////////////////////////////////////////////////

async function onClickAssignReviewers(file) {
    console.log('* clicked Assign Reviewers', file);
    store.msg('Assign reviewers for this file.');
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

// for saving the raw data from the uploaded file
const selected_project_id_for_file = ref();

const upload_file_column_mappings = ref({
    term: '',
    description: '',
    values: '',
});
window.upload_file_column_mappings = upload_file_column_mappings;

let upload_file_data = {};
window.upload_file_data = upload_file_data;

const upload_file_columns = ref([]);

function getSelectionOptions(file) {
    return file.columns.map((col) => {
        return {
            label: '[' + col + ']',
            code: col
        };
    });
}

async function onChangeUploadFile() {
    console.log('* changed file:', fileupload.value.files[0]);
    try {
        if (!fileupload.value.files.length) {
            store.msg('Please select a file to upload.', 'Error', 'error');
            return;
        }
    } catch (err) {
        store.msg('Please select a file to upload.', 'Error', 'error');
        return;
    }

    let file = fileupload.value.files[0];
    
    Papa.parse(file, {
        // config for parsing csv 
        header: true, // Set to true if your CSV has a header row
        skipEmptyLines: true,

        // call back function when parsing is complete
        complete: async (result) => {
            console.log('* read the selected file:', result);

            // update columns
            upload_file_columns.value = result.meta.fields;

            // Create an object representing the file to add to the store
            upload_file_data['concepts'] = result.data;

            // get all basic information
            upload_file_data["filename"] = file.name;
            upload_file_data['project_id'] = selected_project_id_for_file.value? selected_project_id_for_file.value : 'default_project_id';
            upload_file_data["columns"] = result.meta.fields;
            upload_file_data["file_id"] = uuidv4();
            upload_file_data['user_id'] = store.user.user_id;

            // Empty preselected items
            upload_file_data["column_name_term"] = '';
            upload_file_data["column_name_description"] = '';
            upload_file_data["column_name_values"] = '';

            console.log('* generated upload_file_data:', upload_file_data);

            // add a few more information to each row
            upload_file_data['concepts'] = upload_file_data['concepts'].map((row, index) => {
                // row is one line in the csv file
                return {
                    ...row,
                    // user_id: this.userId,
                    file_id: upload_file_data["file_id"],
                    id: index,
                };
            });

            store.msg('Successfully read the file: ' + file.name);
            
        },
    });
}

async function onClickUpload() {
    console.log('* clicked Upload');
    
    // Check if any required column is empty

    // Convert term, description, and value to standard column names
    upload_file_data["column_name_term"] = upload_file_column_mappings.value.term;
    upload_file_data["column_name_description"] = upload_file_column_mappings.value.description;
    upload_file_data["column_name_values"] = upload_file_column_mappings.value.values;

    // pre-processing the raw data
    upload_file_data['concepts'] = upload_file_data['concepts'].map((row) => {
        let new_row = {
            ...row,

            // Convert the column names to standard names
            __term: row[upload_file_data["column_name_term"]],
            __description: row[upload_file_data["column_name_description"]],

            // a temporary column to hold the raw values
            __values: row[upload_file_data["column_name_values"]],
        };
        
        // delete the original columns
        delete new_row[upload_file_data["column_name_term"]];
        delete new_row[upload_file_data["column_name_description"]];
        delete new_row[upload_file_data["column_name_values"]];

        // copy term and description to standard columns
        new_row.term = new_row.__term;
        new_row.description = new_row.__description;

        // now convert values to an array
        try {
            let __values = new_row.__values.trim();

            if (__values == ''){
                new_row.values = [];
            } else {
                new_row.values = new_row.__values.trim().split('|').map((value) => value.trim());
            }
        } catch (err) {
            console.error(err, new_row);
            new_row.values = [];
        }

        // delete temp columns
        delete new_row.__term;
        delete new_row.__description;
        delete new_row.__values;

        return new_row;
    });

    // send this file to backend
    let data = await Jimin.uploadFile(upload_file_data)
    store.msg(data.message);

    // update project list if no projects
    if (store.projects.length == 0) {
        await onClickUpdateProjectList();
        await onClickProjectItem(store.projects[0]);

    } else {
        // update file list
        await onClickProjectItem(store.current_project);
    }

    // close the dialog
    visible_dialog_upload_file.value = false;
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

            <!-- <Button text
                class="menu-button"
                v-tooltip.bottom="'Update project list.'"
                @click="onClickSave">
                <i class="fa-solid fa-rotate menu-icon"></i>
                <span>
                    Update List
                </span>
            </Button> -->
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
                    <Button v-if="project.project_id != 'default_project_id'"
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
        <div class="w-full flex justify-start items-start">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa-solid fa-briefcase"></i>
                        Project

                        <span v-if="store.current_project">
                            [{{ store.current_project.name }}]
                        </span>
                    </div>
                    <div class="panel-subtitle text-sm">
                    </div>
                </div>
            </div>

            <div class="ml-2">
                <Button v-if="store.current_project"
                    severity="secondary"
                    size="small"
                    v-tooltip.bottom="'Upload a new file to this project.'"
                    @click="onClickNewFileForProject(store.current_project)">
                    <i class="fa-solid fa-upload"></i>
                    Add file to [{{ store.current_project.name }}]
                </Button>
            </div>
        </div>
    </template>

    <Tabs value="files">
    <TabList>
        <Tab value="files">
            <i class="fa-regular fa-folder-open"></i>
            Files
            <span v-if="store.files.length > 0">
                ({{ store.files.length }})
            </span>
        </Tab>
        <Tab value="members">
            <i class="fa fa-users"></i>
            Members
        </Tab>
        <Tab value="settings">
            <i class="fa fa-cog"></i>
            Settings
        </Tab>
    </TabList>
    <TabPanels 
        :style="{ height: 'calc(100vh - 21rem)', width: 'calc(100% + 1rem)', overflowY: 'auto' }">

        <!-- tab for mananging files -->
        <TabPanel value="files">
        <div class="flex flex-col h-full">
            <template v-for="file in store.files">
                <div class="w-full file-item flex flex-col py-2">
                    <div class="file-name flex flex-row justify-between">
                        <div class="text-lg font-bold">
                            <i class="fa fa-file"></i>
                            {{ file.filename }}
                        </div>
                        <div class="file-reviewers">
                            Assigned Reviewers: 
                            <i class="fa fa-user"></i>

                            <Button severity="info"
                                size="small"
                                class="ml-2 btn-mini"
                                @click="onClickAssignReviewers(file)"
                                v-tooltip.bottom="'Assign reviewers for this file.'">
                                <i class="fa-solid fa-user-plus"></i>
                                Assign
                            </Button>
                        </div>
                    </div>

                    <div class="file-column flex flex-row mb-2">
                        <div class="flex flex-col mr-2 w-col-select-box">
                            <div class="text-sm">Term Column</div>
                            <p class="text-xl font-bold">
                                {{ file.column_name_term }}
                            </p>
                        </div>

                        <div class="flex flex-col w-col-select-box mr-2">
                            <div class="text-sm">Description Column</div>
                            <p class="text-xl font-bold">
                                {{ file.column_name_description }}
                            </p>
                        </div>

                        <div class="flex flex-col w-col-select-box">
                            <div class="text-sm">Values Column</div>
                            <p class="text-xl font-bold">
                                {{ file.column_name_values }}
                            </p>
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

                        <!-- <Button 
                            severity="help"
                            size="small"
                            class="mr-2"
                            v-tooltip.bottom="'Move this file.'"
                            @click="visible_dialog_move_file = true; selected_file_for_move = file">
                            <i class="fa-solid fa-angles-right"></i>
                            move
                        </Button> -->

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
        </TabPanel>

        <!-- tab for managing reviewers -->
        <TabPanel value="members">
        </TabPanel>

        <!-- tab for managing settings -->
        <TabPanel value="settings">
        </TabPanel>

    </TabPanels>
    </Tabs>
</Panel>


</div>

<!-- Dialog for uploading a new file -->
<Dialog v-model:visible="visible_dialog_upload_file" 
    modal 
    header="Upload file" 
    :style="{ width: '50rem' }">
    <span class="text-surface-500 dark:text-surface-400 block mb-8">
        Upload your .csv file for the following project.
    </span>
    <div class="flex flex-col justify-start gap-4 mb-4">
        <div>
            <label for="select_project" class="font-semibold w-24">
                Select a Project
            </label>
            <Select v-model="selected_project_id_for_file" 
                :options="store.projects"
                optionLabel="name" 
                optionValue="project_id"
                placeholder="Select a project" 
                class="w-full" />
        </div>
        <label for="select_file" class="font-semibold">Select File</label>
        <FileUpload ref="fileupload" 
            mode="basic" name="demo[]" 
            url="/api/upload" 
            @change="onChangeUploadFile"
            accept="text/csv" />
        <div class="flex flex-row mb-2 ">
            <div class="flex flex-col mr-2 w-col-select-box">
                <label for="">Term</label>
                <Select v-model="upload_file_column_mappings.term" 
                    :options="upload_file_columns"
                    placeholder="Select a term column" 
                    class="w-full" />
                <div>
                    <!-- <span v-if="anyDuplicateColumns(file, 'term') != null" 
                        class="text-xs text-red-500">
                        Duplicated with {{ anyDuplicateColumns(file, 'term') }}
                    </span> -->
                </div>
            </div>

            <div class="flex flex-col w-col-select-box mr-2">
                <label for="">Description</label>
                <Select v-model="upload_file_column_mappings.description" 
                    :options="upload_file_columns"
                    placeholder="Select a description column" 
                    class="w-full" />
                <div>
                    <!-- <span v-if="anyDuplicateColumns(file, 'description') != null" 
                        class="text-xs text-red-500">
                        Duplicated with {{ anyDuplicateColumns(file, 'description') }}
                    </span> -->
                </div>
            </div>

            <div class="flex flex-col w-col-select-box">
                <label for="">Value</label>
                <Select v-model="upload_file_column_mappings.values" 
                    :options="upload_file_columns"
                    placeholder="Select a value column" 
                    class="w-full" />
                <div>
                    <!-- <span v-if="anyDuplicateColumns(file, 'value') != null" 
                        class="text-xs text-red-500">
                        Duplicated with {{ anyDuplicateColumns(file, 'value') }}
                    </span> -->
                </div>
            </div>
        </div>
    </div>
    <div class="flex justify-end gap-2">
        <Button label="Upload" @click="onClickUpload()" severity="secondary" />
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

<!-- <Dialog v-model:visible="visible_dialog_move_file" 
    modal 
    header="Move file" 
    :style="{ width: '25rem' }">
    <span class="text-surface-500 dark:text-surface-400 block mb-8">
        Move this file to another project.
    </span>
    <div class="flex flex-col justify-start gap-4 mb-4">
        <div>
            <label for="select_project" class="font-semibold w-24">
                Select Target Project
            </label>
            <Select v-model="selected_project_for_move" 
                :options="store.projects"
                optionLabel="name" 
                optionValue="project_id"
                placeholder="Select a project" 
                class="w-full" />
        </div>
    </div>
    <div class="flex justify-end gap-2">
        <Button label="Move" @click="onClickMove()" severity="secondary" />
    </div>
</Dialog> -->


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