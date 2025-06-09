// Override base.js
SAVE_PATH = 'fix-items-condition';

function printItemsTableHeader() {
    document.querySelector("#items_table thead").insertAdjacentHTML("beforeend", `
    <tr>
      <th>Barcode</th>
      <th>Shelf Condition</th>
      <th>Result</th>
    </tr>
    `);
}

function addRowForBarcode(barcode) {
    document.querySelector("#items_table tbody").insertAdjacentHTML("beforeend", `
        <tr>
            <td class="barcode">${barcode}</td>
            <td class="shelf_condition"><em>Remove condition note</em></td>
            <td class="result"></td>
        </tr>
        `);
}

function rowsToData(rows) {
    return rows.map((tr) => {
        return {
            barcode: tr.querySelector('.barcode').textContent,
        }
    });
}
