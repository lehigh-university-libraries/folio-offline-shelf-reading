
const SHELF_STATUS_PRESENT = "Present";
const SHELF_STATUS_MISSING = "Missing";
const SHELF_STATUS_NOT_AVAILABLE = "Unavailable item is on shelf";
const SHELF_STATUS_IGNORE_INVENTORIED = "Ignoring: Already inventoried";

const ITEM_STATUS_ALREADY_INVENTORIED = "Already inventoried";

const BATCH_SIZE = 20;

// https://stackoverflow.com/a/23395136
const BEEP = new Audio("data:audio/wav;base64,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qJrx4KOQjahZxWbcZgztj2c49nKmkId44S71j0c8eV9yDK6uPRzx5X18eDvjvQ6yKo9ZSS6l//8elePK/Lf//IInrOF/FvDoADYAGBMGb7FtErm5MXMlmPAJQVgWta7Zx2go+8xJ0UiCb8LHHdftWyLJE0QIAIsI+UbXu67dZMjmgDGCGl1H+vpF4NSDckSIkk7Vd+sxEhBQMRU8j/12UIRhzSaUdQ+rQU5kGeFxm+hb1oh6pWWmv3uvmReDl0UnvtapVaIzo1jZbf/pD6ElLqSX+rUmOQNpJFa/r+sa4e/pBlAABoAAAAA3CUgShLdGIxsY7AUABPRrgCABdDuQ5GC7DqPQCgbbJUAoRSUj+NIEig0YfyWUho1VBBBA//uQZB4ABZx5zfMakeAAAAmwAAAAF5F3P0w9GtAAACfAAAAAwLhMDmAYWMgVEG1U0FIGCBgXBXAtfMH10000EEEEEECUBYln03TTTdNBDZopopYvrTTdNa325mImNg3TTPV9q3pmY0xoO6bv3r00y+IDGid/9aaaZTGMuj9mpu9Mpio1dXrr5HERTZSmqU36A3CumzN/9Robv/Xx4v9ijkSRSNLQhAWumap82WRSBUqXStV/YcS+XVLnSS+WLDroqArFkMEsAS+eWmrUzrO0oEmE40RlMZ5+ODIkAyKAGUwZ3mVKmcamcJnMW26MRPgUw6j+LkhyHGVGYjSUUKNpuJUQoOIAyDvEyG8S5yfK6dhZc0Tx1KI/gviKL6qvvFs1+bWtaz58uUNnryq6kt5RzOCkPWlVqVX2a/EEBUdU1KrXLf40GoiiFXK///qpoiDXrOgqDR38JB0bw7SoL+ZB9o1RCkQjQ2CBYZKd/+VJxZRRZlqSkKiws0WFxUyCwsKiMy7hUVFhIaCrNQsKkTIsLivwKKigsj8XYlwt/WKi2N4d//uQRCSAAjURNIHpMZBGYiaQPSYyAAABLAAAAAAAACWAAAAApUF/Mg+0aohSIRobBAsMlO//Kk4soosy1JSFRYWaLC4qZBYWFRGZdwqKiwkNBVmoWFSJkWFxX4FFRQWR+LsS4W/rFRb/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////VEFHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAU291bmRib3kuZGUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMjAwNGh0dHA6Ly93d3cuc291bmRib3kuZGUAAAAAAAAAACU=");

let conditionsMap;
let itemBarcodes;
let currentRow;
let expectedRow;

let unknownBarcodes = [];

addEventListener("load", (event) => {
  loadConditions();
});

async function loadConditions() {
  const response = await fetch('/load-conditions');
  if (!response.ok) {
    throw new Error(`Response: ${response.status} ${await response.text()}`);
  }

  const conditions = await response.json();
  conditionsMap = new Map(conditions);
}

async function loadItems() {
  try {
    const params = new URLSearchParams();
    params.append("start_barcode", document.getElementById("start_barcode").value);
    params.append("end_barcode", document.getElementById("end_barcode").value);
    const response = await fetch(`/load-items?${params}`);
    if (!response.ok) {
      throw new Error(`Response: ${response.status} ${await response.text()}`);
    }

    const items = await response.json();
    itemBarcodes = items.map((item) => item.barcode);

    printItemsTable(items);
    setExpectedRow(1);
  } catch (error) {
    beep(error.message);
  }
}

function printItemsTable(items) {
  printItemsTableHeader();
  for (item of items) {
    const callNumber = item.item_call_number ?? item.holdings_call_number;
    let itemStatus = item.item_status == 'Available' ? '' : item.item_status;
    let alreadyInventoried = false;
    if (item.local_inventoried) {
      if (itemStatus.length) {
        itemStatus += ', ';
      }
      itemStatus += ITEM_STATUS_ALREADY_INVENTORIED; 
      alreadyInventoried = true;
    }
    document.querySelector("#items_table tbody").insertAdjacentHTML("beforeend", `
      <tr
        data-item-id="${item.id}"
        ${alreadyInventoried ? 'class="already-inventoried"' : ''}
      >
        <td class="barcode">${item.barcode}</td>
        <td class="call_number">${callNumber}</td>
        <td class="item_status">${itemStatus}</td>
        <td>${item.title}</td>
        <td class="shelf_status"></td>
        <td class="shelf_condition"></td>
        <td class="result"></td>
      </tr>
    `);
  }
  document.getElementById("next_barcode").focus();
}

function printItemsTableHeader() {
  document.querySelector("#items_table thead").insertAdjacentHTML("beforeend", `
    <tr>
      <th>Barcode</th>
      <th>Call Number</th>
      <th>Item<br/>Status</th>
      <th>Title</th>
      <th>Shelf Status</th>
      <th>Shelf Condition</th>
      <th>Result</th>
    </tr>
    `);
}

function scanNextBarcode() {
  const barcode = document.getElementById("next_barcode").value;
  if (isConditionBarcode(barcode)) {
    processConditionBarcode(barcode);
  }
  else {
    processItemBarcode(barcode);
  }

  document.getElementById("next_barcode").value = null;
  document.getElementById("next_barcode").focus();
}

function processItemBarcode(barcode) {
  const scannedRow = getRowForBarcode(barcode);
  if (scannedRow < 1) {
    beep("Barcode not found in this range.\n\nPlease move the item to the cart.");
    unknownBarcodes.push(barcode)
    return;
  }

  currentRow = scannedRow;
  const itemStatus = document
    .querySelector(`#items_table tbody tr:nth-child(${currentRow}) td.item_status`)
    .textContent;
  if (currentRow == expectedRow) {
    processScannedRow(currentRow, itemStatus);
    setExpectedRow(expectedRow + 1);
  }
  else if (currentRow > expectedRow) {
    for (skippedRow = expectedRow; skippedRow < currentRow; skippedRow++) {
      processSkippedRow(skippedRow);
    }
    processScannedRow(currentRow, itemStatus);
    setExpectedRow(currentRow + 1);
  }
  else {
    beep("The scanned item was misplaced; it should be shelved earlier in this range.\n\nPlease re-shelve it now.")
    processScannedRow(currentRow, itemStatus);
  }
}

function processScannedRow(row, itemStatus) {
  if (itemStatus.includes(ITEM_STATUS_ALREADY_INVENTORIED)) {
    setShelfStatus(row, SHELF_STATUS_IGNORE_INVENTORIED);
  }
  else if (itemStatus.length > 0) {
    setShelfStatus(row, SHELF_STATUS_NOT_AVAILABLE);
  }
  else {
    setShelfStatus(currentRow, SHELF_STATUS_PRESENT);
  }
}

function processSkippedRow(skippedRow) {
  const skippedRowitemStatus = document
    .querySelector(`#items_table tbody tr:nth-child(${skippedRow}) td.item_status`)
    .textContent;
  if (skippedRowitemStatus.includes(ITEM_STATUS_ALREADY_INVENTORIED)) {
    setShelfStatus(skippedRow, SHELF_STATUS_IGNORE_INVENTORIED);
  }
  else {
    setShelfStatus(skippedRow, SHELF_STATUS_MISSING);
  }
}

function getRowForBarcode(barcode) {
  return itemBarcodes.indexOf(barcode) + 1;
}

function setShelfStatus(row, value) {
  const tr = document.querySelector(`#items_table tbody tr:nth-child(${row})`);
  tr.querySelector(`td.shelf_status`).textContent = value;
  tr.classList.add("marked");
  if (value.includes("Ignoring")) {
    tr.classList.add("ignore");
  }
}

function setCondition(row, value) {
  const td = document.querySelector(`#items_table tbody tr:nth-child(${row}) td.shelf_condition`);
  td.textContent = value.trim();
}

function setExpectedRow(row) {
  expectedRow = row;
  document.querySelectorAll("#items_table tbody tr").forEach((tr) => {
    tr.classList.remove("expected");
  });
  document.querySelector(`#items_table tbody tr:nth-child(${row})`).classList.add("expected");
}

function isConditionBarcode(barcode) {
  return conditionsMap.has(barcode);
}

function processConditionBarcode(conditionBarcode) {
  const condition = conditionsMap.get(conditionBarcode);
  setCondition(currentRow, condition);
}

function saveToFolio() {
  const rows = document.querySelectorAll(
    "#items_table tbody tr.marked:not(.already-inventoried):not(.result-success):not(.ignore)"
  );
  let start = 0;
  while (start < rows.length) {
    const batch = Array.from(rows).slice(start, start + BATCH_SIZE);
    if (batch.length > 0) {
      saveBatch(batch);
    }
    start += BATCH_SIZE;
  }

  reportResults();
}

async function saveBatch(batch) {
  const payload = rowsToData(batch);
  try {
    const response = await fetch('/save-items', {
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
    beep(error.message);
  }
};

function rowsToData(rows) {
  return rows.map((tr) => {
    return {
      id: tr.dataset.itemId,
      barcode: tr.querySelector('.barcode').textContent,
      item_status: tr.querySelector('.item_status').textContent,
      shelf_status: tr.querySelector('.shelf_status').textContent,
      shelf_condition: tr.querySelector('.shelf_condition').textContent,
    }
  });
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

async function reportResults() {
  const itemsInput = rowsToData(Array.from(document.querySelectorAll('#items_table tbody tr.marked')));

  const payload = {
    itemsInput: itemsInput,
    unknownBarcodes: unknownBarcodes,
  };
  try {
    const response = await fetch('/report-results', {
      method: "POST",
      body: JSON.stringify(payload),
      headers: {
        'Content-Type': 'application/json', 
      },
    });
    if (!response.ok) {
      throw new Error(`Response: ${response.status} ${await response.text()}`);
    }
  } catch (error) {
    beep(error.message);
  }
}

function beep(text) {
  BEEP.play();
  alert(text);
}
