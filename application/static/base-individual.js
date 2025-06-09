addEventListener("load", (event) => {
    document.getElementById("next_barcode").disabled = false;
    document.getElementById("next_barcode").focus();

    printItemsTableHeader();
    document.querySelector(".table_section").style.display = 'initial';

    itemBarcodes = [];
});

function processItemBarcode(barcode) {
    addRowForBarcode(barcode);
    previousScannedRow = document.querySelectorAll("#items_table tbody tr").length;
    itemBarcodes.push(barcode);
    document.getElementById("save_to_folio").disabled = false;
}

function saveToFolio() {
    const rows = document.querySelectorAll(
        "#items_table tbody tr:not(.result-success)"
    );
    saveBatches(rows);
}
