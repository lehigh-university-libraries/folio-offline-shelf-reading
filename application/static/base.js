
const CUSTOM_CONDITION = "<custom>";
const BATCH_SIZE = 20;

// Attribution in README.md
const BEEP_GOOD = new Audio("static/beep-313342.mp3");
const BEEP_BAD = new Audio("static/message-notification-103496.mp3");

let SAVE_PATH = 'save-items';

let modeValue;
let itemBarcodes;
let previousScannedRow;
let conditionsMap;

addEventListener("load", (event) => {
  loadConditions();
  modeValue = document.querySelector("#mode_select option:checked").value;
});

document.getElementById("mode_select").addEventListener("change", (event) => {
  const saveEnabled = !document.getElementById("save_to_folio").disabled;
  if (saveEnabled) {
    const ok = confirm("Switching to a different mode will discard any scanned items below that have not yet been saved to FOLIO.  Are you sure?");
    if (!ok) {
      document.getElementById("mode_select").value = modeValue;
      return;
    }
  }

  const selected = document.querySelector("#mode_select option:checked");
  const href = selected.value;
  document.location.href = href;
})

async function loadConditions() {
  const response = await fetch('load-conditions');
  if (!response.ok) {
    throw new Error(`Response: ${response.status} ${await response.text()}`);
  }

  const conditions = await response.json();
  conditionsMap = new Map(conditions);
}

function isConditionBarcode(barcode) {
  return conditionsMap.has(barcode);
}

function scanNextBarcode() {
  const barcode = document.getElementById("next_barcode").value;
  if (!validateBarcode(barcode)) {
    document.getElementById("next_barcode").value = null;
    return;
  }

  if (isConditionBarcode(barcode)) {
    processConditionBarcode(barcode);
  }
  else {
    processItemBarcode(barcode);
  }

  document.getElementById("next_barcode").value = null;
  document.getElementById("next_barcode").focus();
}

function validateBarcode(barcode, label = "barcode") {
  const regex = new RegExp(VALIDATION_BARCODE);
  const result = regex.test(barcode);
  if (!result) {
    beepBad("Invalid " + label + ": " + barcode);
  }
  return result;
}

function processConditionBarcode(conditionBarcode) {
  let condition = conditionsMap.get(conditionBarcode);
  if (condition == CUSTOM_CONDITION) {
    condition = prompt("Please enter notes on the item's condition.");
    const regex = new RegExp(VALIDATION_SHELF_CONDITION);
    const result = regex.test(condition);
    if (!result) {
      beepBad("Cannot use that custom condition.  It includes some unsupported characters.");
      return;
    }
  }
  setCondition(previousScannedRow, condition);
}

function setCondition(row, value) {
  const td = document.querySelector(`#items_table tbody tr:nth-child(${row}) td.shelf_condition`);
  td.textContent = value.trim();
}

function saveBatches(rows) {
  let start = 0;
  while (start < rows.length) {
    const batch = Array.from(rows).slice(start, start + BATCH_SIZE);
    if (batch.length > 0) {
      saveBatch(batch);
    }
    start += BATCH_SIZE;
  }
}

async function saveBatch(batch) {
  const payload = rowsToData(batch);
  setWaiting(true);
  try {
    const response = await fetch(SAVE_PATH, {
      method: "POST",
      body: JSON.stringify(payload),
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error(`Response: ${response.status} ${await response.text()}`);
    }
    const results = await response.json();
    printResults(results);
  } catch (error) {
    beepBad(error.message);
  } finally {
    setWaiting(false);
  }
};

function getRowForBarcode(barcode) {
  return itemBarcodes.indexOf(barcode) + 1;
}

function printResults(results) {
  for (result of results) {
    const row = getRowForBarcode(result.barcode);
    const tr = document.querySelector(`#items_table tbody tr:nth-child(${row})`);
    if (result.success) {
      tr.classList.add('result-success');
    }
    else {
      tr.classList.add('result-failure');
    }
    const td = tr.querySelector('td.result');
    td.textContent = result.text;
  }
}

async function logout() {
  try {
    const response = await fetch('logout', {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Basic fake',
      },
    });
    if (response.status != 401) {
      throw new Error(`Response: ${response.status} ${await response.text()}`);
    }
    location.href = "done/logout";
  } catch (error) {
    beep(error.message);
  }
}

function beepBad(text) {
  BEEP_BAD.play();
  alert(text);
}

function beepGood() {
  BEEP_GOOD.play();
}

function setWaiting(isWaiting) {
  if (isWaiting) {
    document.body.classList.add("waiting");
  }
  else {
    document.body.classList.remove("waiting");
  }
}
