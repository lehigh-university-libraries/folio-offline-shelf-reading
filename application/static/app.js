
// If changing any of these values, check for changes in app.py as well.
const SHELF_STATUS_PRESENT = "Present";
const SHELF_STATUS_MISSING = "Missing";
const SHELF_STATUS_UNAVAILABLE_BUT_ON_SHELF = "Unavailable item is on shelf";
const SHELF_STATUS_UNAVAILABLE_AS_EXPECTED = "Unavailable as expected";
const SHELF_STATUS_IGNORE_INVENTORIED = "Ignoring: Already inventoried";

const ITEM_STATUS_ALREADY_INVENTORIED = "Already inventoried";

const CUSTOM_CONDITION = "<custom>";

const BATCH_SIZE = 20;

// Attribution in README.md
const BEEP_GOOD = new Audio("static/beep-313342.mp3");
const BEEP_BAD = new Audio("static/message-notification-103496.mp3");

let conditionsMap;
let itemBarcodes;
let previousScannedRow;
let firstScannedRow = false;
let lastScannedRow = false;

let unknownBarcodes = [];

addEventListener("load", (event) => {
  loadConditions();
  document.getElementById("start_barcode").focus();
});

async function loadConditions() {
  const response = await fetch('load-conditions');
  if (!response.ok) {
    throw new Error(`Response: ${response.status} ${await response.text()}`);
  }

  const conditions = await response.json();
  conditionsMap = new Map(conditions);
}

async function loadItems() {
  // Ensure both range barcodes are entered before loading
  if (!document.getElementById("start_barcode").value.length) {
    return;
  }
  if (!document.getElementById("end_barcode").value.length) {
    document.getElementById("end_barcode").focus();
    return;
  }

  try {
    const params = new URLSearchParams();
    params.append("start_barcode", document.getElementById("start_barcode").value);
    params.append("end_barcode", document.getElementById("end_barcode").value);
    const response = await fetch(`load-items?${params}`);
    if (!response.ok) {
      throw new Error(`Response: ${response.status} ${await response.text()}`);
    }

    const items = await response.json();
    if (!items.length) {
      beepBad('No items in this range.');
      return;
    }

    itemBarcodes = items.map((item) => item.barcode);

    printItemsTable(items);
    setExpectedRow(1);
    document.querySelector("#load-items input[type=submit]").disabled = true;
  } catch (error) {
    beepBad(error.message);
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

  // Check for out-of-range items
  if (scannedRow < 1) {
    beepBad("Barcode not found in this range.\n\nPlease move the item to the cart.");
    unknownBarcodes.push(barcode)
    return;
  }

  const tr = document.querySelector(`#items_table tbody tr:nth-child(${scannedRow})`)
  const itemStatus = tr.querySelector(`td.item_status`).textContent;
  tr.scrollIntoView();

  // Process scanned item
  processScannedRow(scannedRow, itemStatus);
  setExpectedRow(scannedRow + 1);

  // Check for out-of-order items
  if (scannedRow < previousScannedRow) {
    beepBad("Check and fix the shelving order of the last two books scanned.")
  }
  else {
    beepGood();
  }

  // Store range of has been scanned
  previousScannedRow = scannedRow;
  if (!firstScannedRow || scannedRow < firstScannedRow) {
    firstScannedRow = scannedRow;
  }
  if (!lastScannedRow || scannedRow > lastScannedRow) {
    lastScannedRow = scannedRow;
  }
}

function processScannedRow(row, itemStatus) {
  if (itemStatus.includes(ITEM_STATUS_ALREADY_INVENTORIED)) {
    setShelfStatus(row, SHELF_STATUS_IGNORE_INVENTORIED);
  }
  else if (itemStatus.length > 0) {
    setShelfStatus(row, SHELF_STATUS_UNAVAILABLE_BUT_ON_SHELF);
  }
  else {
    setShelfStatus(row, SHELF_STATUS_PRESENT);
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
  document.querySelectorAll("#items_table tbody tr.expected").forEach((tr) => {
    tr.classList.remove("expected");
  });
  if (row <= itemBarcodes.length) {
    document.querySelector(`#items_table tbody tr:nth-child(${row})`).classList.add("expected");
  }
}

function isConditionBarcode(barcode) {
  return conditionsMap.has(barcode);
}

function processConditionBarcode(conditionBarcode) {
  let condition = conditionsMap.get(conditionBarcode);
  if (condition == CUSTOM_CONDITION) {
    condition = prompt("Please enter notes on the item's condition.");
  }
  setCondition(previousScannedRow, condition);
}

function saveToFolio() {
  processSkippedRows();

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

function processSkippedRows() {
  for (let row = firstScannedRow; row <= lastScannedRow; row++) {
    const tr = document.querySelector(`#items_table tbody tr:nth-child(${row}):not(.marked):not(.already-inventoried):not(.result-success)`);
    if (tr) {
      const itemStatus = tr.querySelector("td.item_status").textContent;
      if (!itemStatus.length) {
        setShelfStatus(row, SHELF_STATUS_MISSING);
      }
      else {
        setShelfStatus(row, SHELF_STATUS_UNAVAILABLE_AS_EXPECTED);
      }
    }
  }
}

async function saveBatch(batch) {
  const payload = rowsToData(batch);
  try {
    const response = await fetch('save-items', {
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
  }
};

function rowsToData(rows) {
  return rows.map((tr) => {
    return {
      id: tr.dataset.itemId,
      barcode: tr.querySelector('.barcode').textContent,
      item_status: tr.querySelector('.item_status').textContent,
      call_number: tr.querySelector('.call_number').textContent,
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
    const response = await fetch('report-results', {
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
    beepBad(error.message);
  }
}

function beepBad(text) {
  BEEP_BAD.play();
  alert(text);
}

function beepGood() {
  BEEP_GOOD.play();
}
