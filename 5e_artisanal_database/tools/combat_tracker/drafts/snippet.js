// Combat Tracker Player View Sync Snippet
// Copy and paste this into the browser console on the DM tracker page
// to enable real-time sync with the player-facing view

// Function to sync data to player view
function syncToPlayerView() {
    const syncData = {
        combatants: combatants.map(c => ({
            name: c.name,
            initiative: c.initiative,
            id: c.id,
            currentHp: c.currentHp,
            maxHp: c.maxHp,
            conditions: c.conditions || []
        })),
        currentTurnIndex: currentTurnIndex,
        timestamp: Date.now()
    };

    localStorage.setItem('combatTrackerSync', JSON.stringify(syncData));
    console.log('Synced to player view:', syncData);
}

// Store original functions
const originalAddCombatant = window.addCombatant;
const originalNextTurn = window.nextTurn;
const originalUpdateInitiative = window.updateInitiative;
const originalRemoveCombatant = window.removeCombatant;
const originalResetCombat = window.resetCombat;
const originalRenderCombatTable = window.renderCombatTable;

// Override addCombatant to include sync
window.addCombatant = function() {
    originalAddCombatant.apply(this, arguments);
    syncToPlayerView();
};

// Override nextTurn to include sync
window.nextTurn = function() {
    originalNextTurn.apply(this, arguments);
    syncToPlayerView();
};

// Override updateInitiative to include sync
window.updateInitiative = function() {
    originalUpdateInitiative.apply(this, arguments);
    syncToPlayerView();
};

// Override removeCombatant to include sync
window.removeCombatant = function() {
    originalRemoveCombatant.apply(this, arguments);
    syncToPlayerView();
};

// Override resetCombat to include sync
window.resetCombat = function() {
    originalResetCombat.apply(this, arguments);
    syncToPlayerView();
};

// Override renderCombatTable to include sync (this catches other updates)
window.renderCombatTable = function() {
    originalRenderCombatTable.apply(this, arguments);
    syncToPlayerView();
};

// Conditions system
const CONDITIONS = {
    'Blinded': '🙈',
    'Charmed': '😍',
    'Deafened': '🙉',
    'Exhaustion': '🥵',
    'Frightened': '😱',
    'Grappled': '⛓️',
    'Incapacitated': '🚫',
    'Invisible': '🌫️',
    'Paralyzed': '🥶',
    'Petrified': '🪨',
    'Poisoned': '🤢',
    'Prone': '🛌',
    'Restrained': '🕸️',
    'Stunned': '💫',
    'Unconscious': '😴'
};

// Add condition to combatant
function addCondition(combatantId, condition) {
    const combatant = combatants.find(c => c.id === combatantId);
    if (combatant) {
        if (!combatant.conditions) combatant.conditions = [];
        if (!combatant.conditions.includes(condition)) {
            combatant.conditions.push(condition);
            renderCombatTable();
            syncToPlayerView();
        }
    }
}

// Remove condition from combatant
function removeCondition(combatantId, condition) {
    const combatant = combatants.find(c => c.id === combatantId);
    if (combatant && combatant.conditions) {
        combatant.conditions = combatant.conditions.filter(c => c !== condition);
        renderCombatTable();
        syncToPlayerView();
    }
}

// Generate conditions display HTML
function getConditionsDisplay(combatant) {
    if (!combatant.conditions || combatant.conditions.length === 0) {
        return '';
    }

    return combatant.conditions.map(condition =>
        `<span onclick="removeCondition(${combatant.id}, '${condition}')"
               style="cursor: pointer; margin-right: 4px; font-size: 16px;"
               title="Click to remove ${condition}">${CONDITIONS[condition]}</span>`
    ).join('');
}

// Add conditions column to table header
function addConditionsHeader() {
    const thead = document.querySelector('#combatTable thead tr');
    if (thead && !thead.querySelector('.conditions-col')) {
        const conditionsHeader = document.createElement('th');
        conditionsHeader.className = 'conditions-col';
        conditionsHeader.style.width = '110px';
        conditionsHeader.textContent = 'Conditions';
        thead.insertBefore(conditionsHeader, thead.firstChild);
    }
}

// Override renderCombatTable to include conditions
const originalRenderCombatTableFunc = window.renderCombatTable;
window.renderCombatTable = function() {
    // Ensure header is updated first
    addConditionsHeader();

    const tbody = document.getElementById('combatBody');
    tbody.innerHTML = '';

    combatants.forEach((combatant, index) => {
        const row = document.createElement('tr');

        // Add current turn highlighting
        if (index === currentTurnIndex && combatants.length > 0) {
            row.classList.add('current-turn');
        }

        // Create conditions dropdown
        const conditionsDropdown = `
            <select onchange="if(this.value) { addCondition(${combatant.id}, this.value); this.value = ''; }"
                    style="width: 100px; font-size: 12px; padding: 2px;">
                <option value="">+ Condition</option>
                ${Object.keys(CONDITIONS).map(condition =>
                    `<option value="${condition}">${CONDITIONS[condition]} ${condition}</option>`
                ).join('')}
            </select>
        `;

        row.innerHTML = `
            <td style="width: 110px; padding: 4px;">${conditionsDropdown}</td>
            <td><input type="number" value="${combatant.initiative}" onchange="updateInitiative(${combatant.id}, this.value)" class="transparent-input" min="1" max="30"></td>
            <td style="position: relative; padding-right: 100px;">
                <div style="display: flex; align-items: center; height: 100%;">
                    <input type="text" value="${combatant.name}" onchange="updateName(${combatant.id}, this.value)" class="transparent-input" style="flex: 1;">
                    ${getConditionsDisplay(combatant)}

                    ${getMonsterLink ? getMonsterLink(combatant) : ''}
                    <button onclick="removeCombatant(${combatant.id})" title="Remove" class="remove-button" style="position: absolute; right: 5px; font-size: 18px !important; font-weight: bold; line-height: 18px !important; padding: 4px 10px !important;">×</button>
                </div>
            </td>
            <td><input type="number" value="${combatant.ac || ''}" onchange="updateAC(${combatant.id}, this.value)" class="transparent-input" min="1" max="30" placeholder="-"></td>
            ${combatant.maxHp ? `<td>
                <div class="hp-controls">
                    <button onclick="modifyHp(${combatant.id}, 5)" class="hp-button">+5</button>
                    <button onclick="modifyHp(${combatant.id}, 1)" class="hp-button">+1</button>
                    <input type="text" value="${combatant.currentHp}" onchange="setHp(${combatant.id}, this.value)" class="hp-input">
                    <span style="font-size: 16px;">/ </span>
                    <input type="number" value="${combatant.maxHp}" onchange="setMaxHp(${combatant.id}, this.value)" min="1" class="hp-input">
                    <button onclick="modifyHp(${combatant.id}, -1)" class="hp-button">-1</button>
                    <button onclick="modifyHp(${combatant.id}, -5)" class="hp-button">-5</button>
                </div>
            </td>` : '<td>-</td>'}
        `;

        tbody.appendChild(row);
    });

    // Also call sync after rendering
    syncToPlayerView();
};

// Make functions globally available
window.addCondition = addCondition;
window.removeCondition = removeCondition;
window.getConditionsDisplay = getConditionsDisplay;

// Initial sync
syncToPlayerView();

console.log('Combat Tracker Player View Sync enabled!');
console.log('Open the player view at: combat_tracker_player_facing.html');

// ========================================
// BOOKMARKLET VERSION
// ========================================
// Save this as a bookmark with the following URL:
// javascript:(function(){if(window.combatTrackerSyncEnabled){alert('Combat Tracker sync already enabled!');return;}const CONDITIONS={'Blinded':'🙈','Charmed':'😍','Deafened':'🙉','Exhaustion':'🥵','Frightened':'😱','Grappled':'⛓️','Incapacitated':'🚫','Invisible':'🌫️','Paralyzed':'🥶','Petrified':'🪨','Poisoned':'🤢','Prone':'🛌','Restrained':'🕸️','Stunned':'💫','Unconscious':'😴'};function syncToPlayerView(){const syncData={combatants:combatants.map(c=>({name:c.name,initiative:c.initiative,id:c.id,currentHp:c.currentHp,maxHp:c.maxHp,conditions:c.conditions||[]})),currentTurnIndex:currentTurnIndex,timestamp:Date.now()};localStorage.setItem('combatTrackerSync',JSON.stringify(syncData));console.log('Synced to player view:',syncData);}function addCondition(combatantId,condition){const combatant=combatants.find(c=>c.id===combatantId);if(combatant){if(!combatant.conditions)combatant.conditions=[];if(!combatant.conditions.includes(condition)){combatant.conditions.push(condition);renderCombatTable();syncToPlayerView();}}}function removeCondition(combatantId,condition){const combatant=combatants.find(c=>c.id===combatantId);if(combatant&&combatant.conditions){combatant.conditions=combatant.conditions.filter(c=>c!==condition);renderCombatTable();syncToPlayerView();}}function getConditionsDisplay(combatant){if(!combatant.conditions||combatant.conditions.length===0){return '';}return combatant.conditions.map(condition=>`<span onclick="removeCondition(${combatant.id},'${condition}')" style="cursor:pointer;margin-right:4px;font-size:16px;" title="Click to remove ${condition}">${CONDITIONS[condition]}</span>`).join('');}function addConditionsHeader(){const thead=document.querySelector('#combatTable thead tr');if(thead&&!thead.querySelector('.conditions-col')){const conditionsHeader=document.createElement('th');conditionsHeader.className='conditions-col';conditionsHeader.style.width='110px';conditionsHeader.textContent='Conditions';thead.insertBefore(conditionsHeader,thead.firstChild);}}if(!window.originalCombatFunctions){window.originalCombatFunctions={addCombatant:window.addCombatant,nextTurn:window.nextTurn,updateInitiative:window.updateInitiative,removeCombatant:window.removeCombatant,resetCombat:window.resetCombat,renderCombatTable:window.renderCombatTable};}window.renderCombatTable=function(){addConditionsHeader();const tbody=document.getElementById('combatBody');tbody.innerHTML='';combatants.forEach((combatant,index)=>{const row=document.createElement('tr');if(index===currentTurnIndex&&combatants.length>0){row.classList.add('current-turn');}const conditionsDropdown=`<select onchange="if(this.value){addCondition(${combatant.id},this.value);this.value='';}" style="width:100px;font-size:12px;padding:2px;"><option value="">+ Condition</option>${Object.keys(CONDITIONS).map(condition=>`<option value="${condition}">${CONDITIONS[condition]} ${condition}</option>`).join('')}</select>`;row.innerHTML=`<td style="width:110px;padding:4px;">${conditionsDropdown}</td><td><input type="number" value="${combatant.initiative}" onchange="updateInitiative(${combatant.id},this.value)" class="transparent-input" min="1" max="30"></td><td style="position:relative;padding-right:100px;"><div style="display:flex;align-items:center;height:100%;"><input type="text" value="${combatant.name}" onchange="updateName(${combatant.id},this.value)" class="transparent-input" style="flex:1;">${getConditionsDisplay(combatant)}${getMonsterLink?getMonsterLink(combatant):''}<button onclick="removeCombatant(${combatant.id})" title="Remove" class="remove-button" style="position:absolute;right:5px;font-size:18px!important;font-weight:bold;line-height:18px!important;padding:4px 10px!important;">×</button></div></td><td><input type="number" value="${combatant.ac||''}" onchange="updateAC(${combatant.id},this.value)" class="transparent-input" min="1" max="30" placeholder="-"></td>${combatant.maxHp?`<td><div class="hp-controls"><button onclick="modifyHp(${combatant.id},5)" class="hp-button">+5</button><button onclick="modifyHp(${combatant.id},1)" class="hp-button">+1</button><input type="text" value="${combatant.currentHp}" onchange="setHp(${combatant.id},this.value)" class="hp-input"><span style="font-size:16px;">/ </span><input type="number" value="${combatant.maxHp}" onchange="setMaxHp(${combatant.id},this.value)" min="1" class="hp-input"><button onclick="modifyHp(${combatant.id},-1)" class="hp-button">-1</button><button onclick="modifyHp(${combatant.id},-5)" class="hp-button">-5</button></div></td>`:'<td>-</td>'}`;tbody.appendChild(row);});syncToPlayerView();};window.addCombatant=function(){window.originalCombatFunctions.addCombatant.apply(this,arguments);syncToPlayerView();};window.nextTurn=function(){window.originalCombatFunctions.nextTurn.apply(this,arguments);syncToPlayerView();};window.updateInitiative=function(){window.originalCombatFunctions.updateInitiative.apply(this,arguments);syncToPlayerView();};window.removeCombatant=function(){window.originalCombatFunctions.removeCombatant.apply(this,arguments);syncToPlayerView();};window.resetCombat=function(){window.originalCombatFunctions.resetCombat.apply(this,arguments);syncToPlayerView();};window.addCondition=addCondition;window.removeCondition=removeCondition;window.getConditionsDisplay=getConditionsDisplay;syncToPlayerView();window.combatTrackerSyncEnabled=true;alert('Combat Tracker with Conditions enabled!\n\nOpen player view: combat_tracker_player_facing.html');})();

// ========================================
// READABLE BOOKMARKLET CODE (for reference)
// ========================================
/*
javascript:(function(){
    // Check if already enabled
    if(window.combatTrackerSyncEnabled){
        alert('Combat Tracker sync already enabled!');
        return;
    }

    // Conditions system
    const CONDITIONS={'Blinded':'🙈','Charmed':'😍','Deafened':'🙉','Exhaustion':'🥵','Frightened':'😱','Grappled':'⛓️','Incapacitated':'🚫','Invisible':'🌫️','Paralyzed':'🥶','Petrified':'🪨','Poisoned':'🤢','Prone':'🛌','Restrained':'🕸️','Stunned':'💫','Unconscious':'😴'};

    // Sync function
    function syncToPlayerView(){
        const syncData={
            combatants:combatants.map(c=>({
                name:c.name,
                initiative:c.initiative,
                id:c.id,
                currentHp:c.currentHp,
                maxHp:c.maxHp,
                conditions:c.conditions||[]
            })),
            currentTurnIndex:currentTurnIndex,
            timestamp:Date.now()
        };
        localStorage.setItem('combatTrackerSync',JSON.stringify(syncData));
        console.log('Synced to player view:',syncData);
    }

    // Condition management functions
    function addCondition(combatantId,condition){
        const combatant=combatants.find(c=>c.id===combatantId);
        if(combatant){
            if(!combatant.conditions)combatant.conditions=[];
            if(!combatant.conditions.includes(condition)){
                combatant.conditions.push(condition);
                renderCombatTable();
                syncToPlayerView();
            }
        }
    }

    function removeCondition(combatantId,condition){
        const combatant=combatants.find(c=>c.id===combatantId);
        if(combatant&&combatant.conditions){
            combatant.conditions=combatant.conditions.filter(c=>c!==condition);
            renderCombatTable();
            syncToPlayerView();
        }
    }

    function getConditionsDisplay(combatant){
        if(!combatant.conditions||combatant.conditions.length===0){
            return '';
        }
        return combatant.conditions.map(condition=>
            `<span onclick="removeCondition(${combatant.id},'${condition}')"
                   style="cursor:pointer;margin-right:4px;font-size:16px;"
                   title="Click to remove ${condition}">${CONDITIONS[condition]}</span>`
        ).join('');
    }

    // Store original functions (only once)
    if(!window.originalCombatFunctions){
        window.originalCombatFunctions={
            addCombatant:window.addCombatant,
            nextTurn:window.nextTurn,
            updateInitiative:window.updateInitiative,
            removeCombatant:window.removeCombatant,
            resetCombat:window.resetCombat,
            renderCombatTable:window.renderCombatTable
        };
    }

    // Override functions with sync
    window.addCombatant=function(){
        window.originalCombatFunctions.addCombatant.apply(this,arguments);
        syncToPlayerView();
    };

    window.nextTurn=function(){
        window.originalCombatFunctions.nextTurn.apply(this,arguments);
        syncToPlayerView();
    };

    window.updateInitiative=function(){
        window.originalCombatFunctions.updateInitiative.apply(this,arguments);
        syncToPlayerView();
    };

    window.removeCombatant=function(){
        window.originalCombatFunctions.removeCombatant.apply(this,arguments);
        syncToPlayerView();
    };

    window.resetCombat=function(){
        window.originalCombatFunctions.resetCombat.apply(this,arguments);
        syncToPlayerView();
    };

    window.renderCombatTable=function(){
        window.originalCombatFunctions.renderCombatTable.apply(this,arguments);
        syncToPlayerView();
    };

    // Initial sync and mark as enabled
    syncToPlayerView();
    window.combatTrackerSyncEnabled=true;
    alert('Combat Tracker Player View Sync enabled!\n\nOpen player view: combat_tracker_player_facing.html');
})();
*/
