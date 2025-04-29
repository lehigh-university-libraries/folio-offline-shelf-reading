
const SHELF_STATUS_PRESENT = "Present";
const SHELF_STATUS_MISSING = "Missing";

// https://stackoverflow.com/a/23395136
const BEEP = new Audio("data:audio/wav;base64,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qJrx4KOQjahZxWbcZgztj2c49nKmkId44S71j0c8eV9yDK6uPRzx5X18eDvjvQ6yKo9ZSS6l//8elePK/Lf//IInrOF/FvDoADYAGBMGb7FtErm5MXMlmPAJQVgWta7Zx2go+8xJ0UiCb8LHHdftWyLJE0QIAIsI+UbXu67dZMjmgDGCGl1H+vpF4NSDckSIkk7Vd+sxEhBQMRU8j/12UIRhzSaUdQ+rQU5kGeFxm+hb1oh6pWWmv3uvmReDl0UnvtapVaIzo1jZbf/pD6ElLqSX+rUmOQNpJFa/r+sa4e/pBlAABoAAAAA3CUgShLdGIxsY7AUABPRrgCABdDuQ5GC7DqPQCgbbJUAoRSUj+NIEig0YfyWUho1VBBBA//uQZB4ABZx5zfMakeAAAAmwAAAAF5F3P0w9GtAAACfAAAAAwLhMDmAYWMgVEG1U0FIGCBgXBXAtfMH10000EEEEEECUBYln03TTTdNBDZopopYvrTTdNa325mImNg3TTPV9q3pmY0xoO6bv3r00y+IDGid/9aaaZTGMuj9mpu9Mpio1dXrr5HERTZSmqU36A3CumzN/9Robv/Xx4v9ijkSRSNLQhAWumap82WRSBUqXStV/YcS+XVLnSS+WLDroqArFkMEsAS+eWmrUzrO0oEmE40RlMZ5+ODIkAyKAGUwZ3mVKmcamcJnMW26MRPgUw6j+LkhyHGVGYjSUUKNpuJUQoOIAyDvEyG8S5yfK6dhZc0Tx1KI/gviKL6qvvFs1+bWtaz58uUNnryq6kt5RzOCkPWlVqVX2a/EEBUdU1KrXLf40GoiiFXK///qpoiDXrOgqDR38JB0bw7SoL+ZB9o1RCkQjQ2CBYZKd/+VJxZRRZlqSkKiws0WFxUyCwsKiMy7hUVFhIaCrNQsKkTIsLivwKKigsj8XYlwt/WKi2N4d//uQRCSAAjURNIHpMZBGYiaQPSYyAAABLAAAAAAAACWAAAAApUF/Mg+0aohSIRobBAsMlO//Kk4soosy1JSFRYWaLC4qZBYWFRGZdwqKiwkNBVmoWFSJkWFxX4FFRQWR+LsS4W/rFRb/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////VEFHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAU291bmRib3kuZGUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMjAwNGh0dHA6Ly93d3cuc291bmRib3kuZGUAAAAAAAAAACU=");

let conditionsMap;
let itemBarcodes;
let currentRow;
let expectedRow;

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
      itemStatus = 'Already inventoried'; 
      alreadyInventoried = true;
    }
    document.querySelector("#items_table tbody").insertAdjacentHTML("beforeend", `
      <tr
        data-item-id="${item.id}"
        ${alreadyInventoried ? 'class="already-inventoried"' : ''}
      >
        <td class="barcode">${item.barcode}</td>
        <td>${callNumber}</td>
        <td>${itemStatus}</td>
        <td>${item.title}</td>
        <td class="shelf_status"><input type="text" disabled></td>
        <td class="shelf_condition"></td>
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
    return;
  }

  currentRow = scannedRow;
  if (currentRow == expectedRow) {
    setStatus(currentRow, SHELF_STATUS_PRESENT);
    setExpectedRow(expectedRow + 1);
  }
  else if (currentRow > expectedRow) {
    setStatus(currentRow, SHELF_STATUS_PRESENT);
    for (row = expectedRow; row < currentRow; row++) {
      setStatus(row, SHELF_STATUS_MISSING);
    }
    setExpectedRow(currentRow + 1);
  }
  else {
    beep("The scanned item was misplaced; it should be shelved earlier in this range.\n\nPlease re-shelve it now.")
    setStatus(currentRow, SHELF_STATUS_PRESENT);
  }
}

function getRowForBarcode(barcode) {
  return itemBarcodes.indexOf(barcode) + 1;
}

function setStatus(row, value) {
  const input = document.querySelector(`#items_table tbody tr:nth-child(${row}) td.shelf_status input`);
  input.value = value;
}

function setCondition(row, value) {
  const td = document.querySelector(`#items_table tbody tr:nth-child(${row}) td.shelf_condition`);
  td.textContent = value;
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

async function saveToFolio() {
  const rows = document.querySelectorAll("#items_table tbody tr");
  const payload = Array.from(rows).map((tr) => {
    return {
      id: tr.dataset.itemId,
      barcode: tr.querySelector('.barcode').textContent,
      shelf_status: tr.querySelector('.shelf_status input').value,
      shelf_condition: tr.querySelector('.shelf_condition').textContent,
    }
  });
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
  } catch (error) {
    beep(error.message);
  }
};

function beep(text) {
  BEEP.play();
  alert(text);
}
