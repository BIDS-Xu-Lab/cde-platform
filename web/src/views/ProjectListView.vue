<script setup>
import { useDataStore } from '../DataStore';
import Papa from 'papaparse'
import { onMounted, ref } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { Jimin } from '../Jimin';
import * as toolbox from '../toolbox';
import { hasResults } from '../CDEHelper';
import ProjectFileItem from '../components/ProjectFileItem.vue';

const store = useDataStore();
const visible_dialog_upload_file = ref(false);
// const visible_dialog_move_file = ref(false);
// const selected_project_for_move = ref();
// const selected_file_for_move = ref();


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
    let ret = await Jimin.getProjects();

    // update store
    store.projects = ret.projects;
}

async function onClickProjectItem(project) {
    console.log('* clicked Project Item', project);

    // if project is null or undefined, return
    if (!project) {
        return;
    }

    store.current_project = project;

    // get all files for this project
    await store.updateCurrentProjectFiles();
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

    // clear the text field and close the dialog
    new_project.value = {
        name: '',
        description: '',
    };
    visible_dialog_create_project.value = false;
}

///////////////////////////////////////////////////////////
// File Related
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
function anyDuplicateColumns(column, skipField = '') {
    // Return null if the column is empty
    if (!column) return null;

    const mappings = {
        term: 'Term',
        description: 'Description',
        values: 'Values'
    };

    // Check each mapping except the one being modified
    for (const [field, label] of Object.entries(mappings)) {
        if (field !== skipField && upload_file_column_mappings.value[field] === column) {
            return label;
        }
    }
    return null;
}

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
            upload_file_data['project_id'] = selected_project_id_for_file.value? selected_project_id_for_file.value : '';
            upload_file_data["columns"] = result.meta.fields;
            upload_file_data["file_id"] = uuidv4();
            // upload_file_data['user_id'] = store.user.user_id;

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
            // pre-select the term description and value columns
            upload_file_column_mappings.value.term = result.meta.fields[0];
            upload_file_column_mappings.value.description = result.meta.fields[1];
            upload_file_column_mappings.value.values = result.meta.fields[2];
            
            store.msg('Successfully read the file: ' + file.name);
            
        },
    });
}
function isUploadDisabled() {
    return upload_file_column_mappings.value.term === '' ||
           upload_file_column_mappings.value.description === '' ||
           upload_file_column_mappings.value.values === '' ||
           anyDuplicateColumns(upload_file_column_mappings.value.term, 'term') ||
           anyDuplicateColumns(upload_file_column_mappings.value.description, 'description') ||
           anyDuplicateColumns(upload_file_column_mappings.value.values, 'values');
}

async function onClickUpload() {
    console.log('* clicked Upload');
    
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
            // remove leading and trailing white spaces
            let __values = new_row.__values.trim();

            if (__values == ''){
                new_row.values = [];
            } else {
                new_row.values = __values.split('|').map((value) => {
                    // Trim whitespace and remove any surrounding quotes
                    let trimmed = value.trim();
                    if ((trimmed.startsWith('"') && trimmed.endsWith('"')) || 
                        (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
                        trimmed = trimmed.substring(1, trimmed.length - 1);
                    }
                    // Handle any internal quotes that might need escaping
                    trimmed = trimmed.replace(/\\(['"])/g, '$1'); // Replace escaped quotes with actual quotes
                    return trimmed;
                });
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
    upload_file_column_mappings.value = {
        term: '',
        description: '',
        values: '',
    };
    visible_dialog_upload_file.value = false;
};

function filterFilesByStatus(files, status) {
    return files.filter((file) => file.round[file.round.length - 1].stage === status);

}
///////////////////////////////////////////////////////////
// Member management
///////////////////////////////////////////////////////////
const email_add_member = ref('');
const project_roles = ref(["mapper","reviewer"]);
const selected_member_role = ref();

async function onClickAddMember(project) {
    console.log('* clicked Add Member', email_add_member.value, selected_member_role.value);

    let email = email_add_member.value;
    let __email = email.trim();

    if (__email == '') {
        store.msg('Please enter an email address.', 'Error', 'error');
        return;
    }
    if (selected_member_role.value == null) {
        store.msg('Please select a role.', 'Error', 'error');
        return;
    }

    // add this email to the project
    let ret = await Jimin.addUserToProjectByEmail(
        project.project_id,
        email_add_member.value,
        selected_member_role.value,
    )

    if (ret.success) {
        store.msg(ret.message);
    } else {
        // if failed, show the error message and no further action
        store.msg(ret.message, 'Error', 'error');
        return;
    }

    // update the project info
    let data = await Jimin.getProject(project.project_id);
    
    // replace the current project with the updated project
    store.current_project = data.project;

    // also update the project list in the store.projects
    let idx = store.projects.findIndex((p) => p.project_id == project.project_id);
    store.projects[idx] = data.project;
}

const visible_dialog_remove_member = ref();
const selected_delete_member = ref();

async function onclickDeleteButton(member) {
    console.log('* clicked Delete Button');
    visible_dialog_remove_member.value = true;
    selected_delete_member.value = member;
}

async function onclickRemoveMember() {
    const member = selected_delete_member.value;
    console.log('* clicked Remove Member', member);

    // remove this member from the project
    let ret = await Jimin.removeUserFromProject(store.current_project.project_id, member.user_id);
    console.log('* removed member:', ret);

    // update the project info
    let data = await Jimin.getProject(store.current_project.project_id);
    
    // replace the current project with the updated project
    store.current_project = data.project;

    // also update the project list in the store.projects
    let idx = store.projects.findIndex((p) => p.project_id == store.current_project.project_id);
    store.projects[idx] = data.project;

    // close the dialog
    visible_dialog_remove_member.value = false;
    selected_delete_member.value = null;

    store.msg(ret.message);
}

// helper function to check the role of the current user
function checkRole(role) {
    return store.current_project.members.some(member => member.user_id === store.user.user_id && (member.role === role || member.role === 'owner'))
}

function defaultTab(){
    if (checkRole('owner')) {
        return 'files';
    }else if (checkRole('mapper')) {
        return 'mapping_files';
    } else if (checkRole('reviewer')) {
        return 'review_files';
    } else {
        return 'members';
    }
}


async function onClickSaveProject() {
    console.log('* clicked Save Project', store.current_project);

    // send this project to backend
    // let project = await Jimin.updateProject(store.current_project);
    // console.log('* updated project:', project);

    // store.msg('Updated the project: ' + project.name);

    // // update project list
    // onClickUpdateProjectList();
}


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
            <div class="w-full project-item flex flex-row justify-between items-start"
                :class="{ 'current-project': store.current_project?.project_id == project.project_id }">
                <div class="flex flex-row cursor-pointer py-2"
                    style="width: calc(100% - 8rem)"
                    @click="onClickProjectItem(project)">
                    <div class="project-name">
                        <span v-if="project.project_id == store.current_project?.project_id"
                            class="font-bold">
                            <i class="fa fa-folder-open mr-2"></i>
                            {{ project.name }}
                        </span>
                        <span v-else>
                            <i class="fa fa-folder mr-2"></i>
                            {{ project.name }}
                        </span>
                    </div>
                </div>

                <div class="py-2"
                    style="width: 8rem; text-align: right;">
                    <div >
                        <font-awesome-icon icon="far fa-file" />
                        {{ project.n_files }}
                        |

                        <font-awesome-icon icon="far fa-user" />
                        {{ project.members.length }} 
                    </div>
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
                    severity="success"
                    v-tooltip.bottom="'Upload a new file to this project.'"
                    @click="onClickNewFileForProject(store.current_project)">
                    <i class="fa-solid fa-upload"></i>
                    Add file
                </Button>
            </div>
        </div>
    </template>

    <Tabs v-if="store.current_project"
        :value="defaultTab()">
        <TabList>
            <Tab value="files" v-if="checkRole('owner')">
                <i class="fa-regular fa-folder-open"></i>
                Total Files
                <span v-if="store.files.length > 0">
                    ({{ store.files.length }})
                </span>
            </Tab>
            <Tab value="mapping_files" v-if="checkRole('mapper')">
                <i class="fa-regular fa-folder-open"></i>
                Files Mapping
                <span v-if="filterFilesByStatus(store.files, 'mapping').length > 0">
                    ({{ filterFilesByStatus(store.files, "mapping").length }})
                </span>
            </Tab>
            <Tab value="review_files" v-if="checkRole('reviewer')">
                <i class="fa-regular fa-folder-open"></i>
                Files Review
                <span v-if="filterFilesByStatus(store.files, 'reviewing').length > 0">
                    ({{ filterFilesByStatus(store.files, 'reviewing').length }})
                </span>
            </Tab>
            <Tab value="members">
                <i class="fa fa-users"></i>
                Members
                <span v-if="store.current_project.members.length > 0">
                    ({{ store.current_project.members.length }})
                </span>
            </Tab>
            <Tab value="settings" v-if="checkRole('owner')">
                <i class="fa fa-cog"></i>
                Settings
            </Tab>
        </TabList>
        <TabPanels 
            :style="{ height: 'calc(100vh - 21.5rem)', width: 'calc(100% + 1rem)', overflowY: 'auto' }">
            <!-- tab for managing files -->
            <TabPanel value="files">
            <div v-if="store.loading_files" class="flex justify-center items-center h-full mt-20">
                <ProgressSpinner style="width: 100px; height: 100px" strokeWidth="3" fill="transparent"
                animationDuration=".5s" aria-label="Custom ProgressSpinner" />
            </div>
            <div class="flex flex-col h-full" v-else-if="store.files.length === 0">
                <div class="flex flex-row justify-center items-center mt-20">
                    <span class="text-2xl font-bold">
                        This project is empty.
                    </span>
                </div>
            </div>
            <div class="flex flex-col h-full" v-else>
                <template v-for="file in store.files">
                    <ProjectFileItem 
                        :file="file"
                        :view_mode="'file'" />
                </template>
            </div>
            </TabPanel>
            <!-- tab for mananging mapping files -->
            <TabPanel value="mapping_files">
            <div v-if="store.loading_files" class="flex justify-center items-center h-full mt-20">
                <ProgressSpinner style="width: 100px; height: 100px" strokeWidth="3" fill="transparent"
                animationDuration=".5s" aria-label="Custom ProgressSpinner" />
            </div>  
            <div class="flex flex-col h-full" v-else>
                <template v-for="file in filterFilesByStatus(store.files, 'mapping')">
                    <ProjectFileItem 
                        :file="file"
                        :view_mode="'mapping'" />
                </template>
            </div>
            </TabPanel>
            <!-- tab for mananging review files -->
            <TabPanel value="review_files">
            <div v-if="store.loading_files" class="flex justify-center items-center h-full mt-20">
                <ProgressSpinner style="width: 100px; height: 100px" strokeWidth="3" fill="transparent"
                animationDuration=".5s" aria-label="Custom ProgressSpinner" />
            </div>  
            <div class="flex flex-col h-full" v-else>
                <template v-for="file in filterFilesByStatus(store.files, 'reviewing')">
                    <ProjectFileItem 
                            :file="file"
                            :view_mode="'review'" />
                    </template>
                </div>
            </TabPanel>

            <!-- tab for managing reviewers -->
            <TabPanel value="members">
            <div class="flex flex-col h-full">
                <div v-if="store.current_project.user_id === store.user.user_id">
                    <label for=""
                        class="mr-2">
                        Email:
                    </label>
                    <InputText placeholder="Enter an email address"
                        v-model="email_add_member"
                        class="mr-2" />
                    <Select v-model="selected_member_role"
                    placeholder="Select a role"
                    :options="project_roles"
                    style="width: 12rem;"
                    class="mr-2"
                    v-tooltip.right="'Select a role to this project.'" />

                    <Button label="Add member"
                        icon="pi pi-plus"
                        @click="onClickAddMember(store.current_project)"
                        v-tooltip.right="'Search this email in system and add to this project'" />   
                </div>

                <div>
                    <template v-for="member in store.current_project.members">
                        <div class="flex flex-row justify-start py-2 items-center">
                            <div class="mr-4">
                                <Button severity="danger"
                                    v-if="store.current_project.user_id === store.user.user_id"
                                    :disabled="store.user.user_id == member.user_id"
                                    size="small"
                                    @click="onclickDeleteButton(member)"
                                    v-tooltip.bottom="'Remove this member from this project.'">
                                    <i class="fa-solid fa-trash"></i>
                                </Button>
                            </div>
                            <div class="flex flex-row items-center">
                                <i class="fa fa-user"></i>
                                <span class="ml-2">
                                    {{ member.name }}
                                </span>
                                <span class="ml-2">
                                    ({{ member.email }})
                                </span>
                                <span class="ml-2">
                                    Role: {{ member.role }}
                                </span>
                            </div>
                        </div>
                    </template>
                </div>
            </div>
            </TabPanel>

            <!-- tab for managing settings -->
            <TabPanel value="settings" v-if="store.current_project.user_id === store.user.user_id">
            <div class="flex flex-col h-full">
                <div>
                    <Button v-tooltip.bottom="'Save the project information.'"
                        severity="success"
                        @click="onClickSaveProject">
                        <i class="fa-solid fa-save"></i>
                        Save settings
                    </Button>
                </div>

                <div>
                    <div class="text-xl font-bold mt-4 border-b-2">
                        <font-awesome-icon icon="fa-solid fa-cog" />
                        Basic Information
                    </div>
                    <div class="flex flex-col gap-4 mt-4">
                        <div class="max-w-lg">
                            <label for="name" class="font-semibold w-24">
                                Project Name
                            </label>
                            <InputText v-model="store.current_project.name"
                                placeholder="Enter a project name"
                                class="w-full" />
                        </div>
                        
                        <div class="max-w-lg">
                            <label for="name" class="font-semibold w-24">
                                Project Description (optional)
                            </label>
                            <InputText v-model="store.current_project.description"
                                placeholder="Enter a project description"
                                class="w-full" />
                        </div>
                    </div>

                    <!-- danger zone -->
                    <div class="text-xl font-bold mt-4 border-b-2">
                        <font-awesome-icon icon="fa-solid fa-exclamation-triangle" />
                        Danger Zone
                    </div>

                    <div class="border-1">

                        <div class="flex flex-row justify-between mb-4 p-4">
                            <div class="flex flex-col">
                                <div class="font-bold">
                                    Transfer ownership
                                </div>
                                <div>
                                    Transfer this project to another user who have the ability to create projects.
                                </div>
                            </div>
                            <div class="flex flex-row justify-end">
                                <Button severity="danger"
                                    severirty="danger"
                                    class="ml-4"
                                    v-tooltip.bottom="'Transfer this project.'"
                                    @click="store.msg('Transfer this project.')">
                                    <i class="fa-solid fa-trash"></i>
                                    Transfer
                                </Button>
                            </div>
                        </div>

                        <div class="flex flex-row justify-between mb-4 p-4">
                            <div class="flex flex-col">
                                <div class="font-bold">
                                    Delete this project
                                </div>
                                <div>
                                    Once you delete a project, there is no going back. Please be certain.
                                </div>
                            </div>
                            <div class="flex flex-row justify-end">
                                <Button severity="danger"
                                    severirty="danger"
                                    class="ml-4"
                                    v-tooltip.bottom="'Delete this project.'"
                                    @click="onClickDeleteProject(store.current_project)">
                                    <i class="fa-solid fa-trash"></i>
                                    Delete this project
                                </Button>
                            </div>
                        </div>


                    </div>
                </div>
            </div>
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

        <!-- select file to upload -->
        <label for="select_file" class="font-semibold">
            Select File
        </label>
        <FileUpload ref="fileupload" 
            mode="basic"
            url="/api/upload" 
            @change="onChangeUploadFile"
            accept=".csv, .tsv" />

        <!-- select columns -->
        <div class="flex flex-row mb-2 ">
            <div class="flex flex-col mr-2 w-1/3">
                <label for="">Term</label>
                <Select v-model="upload_file_column_mappings.term" 
                    :options="upload_file_columns"
                    placeholder="Select a term column" 
                    class="w-full" />
                <div>
                    <span v-if="anyDuplicateColumns(upload_file_column_mappings.term, 'term') != null" 
                        class="text-xs text-red-500">
                        Duplicated with {{ anyDuplicateColumns(upload_file_column_mappings.term, 'term') }}
                    </span>
                </div>
            </div>

            <div class="flex flex-col w-1/3 mr-2">
                <label for="">Description</label>
                <Select v-model="upload_file_column_mappings.description" 
                    :options="upload_file_columns"
                    placeholder="Select a description column" 
                    class="w-full" />
                <div>
                    <span v-if="anyDuplicateColumns(upload_file_column_mappings.description, 'description') != null" 
                        class="text-xs text-red-500">
                        Duplicated with {{ anyDuplicateColumns(upload_file_column_mappings.description, 'description') }}
                    </span>
                </div>
            </div>

            <div class="flex flex-col w-1/3">
                <label for="">Value</label>
                <Select v-model="upload_file_column_mappings.values" 
                    :options="upload_file_columns"
                    placeholder="Select a value column" 
                    class="w-full" />
                <div>
                    <span v-if="anyDuplicateColumns(upload_file_column_mappings.values, 'values') != null" 
                        class="text-xs text-red-500">
                        Duplicated with {{ anyDuplicateColumns(upload_file_column_mappings.values, 'values') }}
                    </span>
                </div>
            </div>
        </div>
    </div>
    <div class="flex justify-end gap-2">
        <Button label="Upload File" 
            :disabled="isUploadDisabled()"
            icon="pi pi-upload"
            @click="onClickUpload()" 
            severity="secondary" />
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

<Dialog v-model:visible="visible_dialog_remove_member"
    modal 
    header="Remove Member" 
    :style="{ width: '25rem' }">
    <span class="text-surface-500 dark:text-surface-400 block mb-8">
        Are you sure you want to remove this member from this project?
    </span>
    <div class="flex justify-end gap-2">
        <Button severity="danger"
            size="small"
            @click="onclickRemoveMember()"
            v-tooltip.bottom="'Confirm to remove.'">
            <i class="fa-solid fa-trash"> Remove</i>
        </Button>
    </div>
</Dialog>


<!-- Dialog for assign users -->
<!-- <Dialog v-model:visible="visible_dialog_assign_users" 
    modal 
    header="Assign Users" 
    :style="{ width: '25rem' }">
    <span class="text-surface-500 dark:text-surface-400 block mb-8">
        Assign users to this project.
    </span>
    <div class="flex flex-col justify-start gap-4 mb-4">
        <div>
            <label for="select_user" class="font-semibold w-24">
                Select User
            </label>
            <Select v-model="selected_user_for_assign" 
                :options="store.users"
                optionLabel="name" 
                optionValue="user_id"
                placeholder="Select a user" 
                class="w-full" />
        </div>
    </div>
    <div class="flex justify-end gap-2">
        <Button label="Assign" @click="onClickAssign()" severity="secondary" />
    </div>
</Dialog> -->

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
    width: calc(100% - 500px);
}

.project-item {
    border-bottom: 1px solid var(--bd-color);
}
.project-item:hover {
    background-color: var(--bg-color-menu-hover);
}
.current-project {
    background-color: var(--bg-color-selected);
}

.file-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--bd-color);
}

.file-item:hover {
    background-color: var(--bg-color-menu-hover);
}

.w-col-info-box {
    width: 180px !important;
}
</style>