
if (testData['start_barcode']) {
    document.getElementById("start_barcode").value = testData['start_barcode'];
}
if (testData['end_barcode']) {
    document.getElementById("end_barcode").value = testData['end_barcode'];
}

addEventListener("load", (event) => {
    if (testData['start_barcode'] && testData['end_barcode']) {
        document.getElementById("next_barcode").focus();
    }
});

document.body.addEventListener('click', (event) => {
    const target = event.target;
    if (target.matches('td.barcode')) {
        const barcode = target.textContent;
        document.getElementById('next_barcode').value = barcode;
        scanNextBarcode();
    }
});
