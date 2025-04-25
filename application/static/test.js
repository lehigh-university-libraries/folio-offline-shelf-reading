
document.body.addEventListener('click', (event) => { 
    const target = event.target;
    if (target.matches('td.barcode')) {
        const barcode = target.textContent;
        document.getElementById('next_barcode').value = barcode;
        scanNextBarcode();
    }
});
