export const hasResults = function(term) {
    return term.results && term.results.length > 0;
}

export async function onClickRefreshListGetSources() {
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

export function checkSubmitStatus(){
    for (const mapping of Object.values(store.working_mappings)) {
        if (mapping.status === "mapped") {
            return true;
        }
    }
    return false;
}