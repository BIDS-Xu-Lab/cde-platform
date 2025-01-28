export const hasResults = function(term) {
    return term.results && term.results.length > 0;
}

export function checkSubmitStatus(){
    for (const mapping of Object.values(store.working_mappings)) {
        if (mapping.status === "mapped") {
            return true;
        }
    }
    return false;
}