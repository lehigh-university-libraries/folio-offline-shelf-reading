addEventListener("load", (event) => {
  document.getElementById("next_barcode").disabled = false;
  document.getElementById("save_to_folio").disabled = false;
  document.getElementById("next_barcode").focus();

  printItemsTableHeader();
  document.querySelector(".table_section").style.display = 'initial';

  itemBarcodes = [];
});

function printItemsTableHeader() {
  document.querySelector("#items_table thead").insertAdjacentHTML("beforeend", `
    <tr>
      <th>Barcode</th>
      <th>Shelf Status</th>
      <th>Shelf Condition</th>
      <th>Result</th>
    </tr>
    `);
}

function processItemBarcode(barcode) {
  document.querySelector("#items_table tbody").insertAdjacentHTML("beforeend", `
    <tr>
      <td class="barcode">${barcode}</td>
      <td class="shelf_status">${SHELF_STATUS_PRESENT}</td>
      <td class="shelf_condition"></td>
      <td class="result"></td>
    </tr>
    `);
  previousScannedRow = document.querySelectorAll("#items_table tbody tr").length;
  itemBarcodes.push(barcode);
}

function saveToFolio() {
  const rows = document.querySelectorAll(
    "#items_table tbody tr:not(.result-success)"
  );
  saveBatches(rows);
}

function rowsToData(rows) {
  return rows.map((tr) => {
    return {
      barcode: tr.querySelector('.barcode').textContent,
      shelf_status: tr.querySelector('.shelf_status').textContent,
      shelf_condition: tr.querySelector('.shelf_condition').textContent,
    }
  });
}
