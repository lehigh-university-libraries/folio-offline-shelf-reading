
async function loadItems() {
  try {
    const params = new URLSearchParams();
    params.append("start_barcode", document.getElementById("start_barcode").value);
    params.append("end_barcode", document.getElementById("end_barcode").value);
    const response = await fetch(`/load-items?${params}`);
    if (!response.ok) {
      throw new Error(`Response: ${response}`);
    }

    const items = await response.json();
    printItemsTable(items);
  } catch (error) {
    console.error(error.message);
  }

  function printItemsTable(items) {
    printItemsTableHeader();
    for (item of items) {
      const callNumber = item.item_call_number ?? item.holdings_call_number;
      const itemStatus = item.item_status == 'Available' ? '' : item.item_status;
      document.querySelector("#items_table tbody").insertAdjacentHTML("beforeend", `
        <tr>
          <td>${item.barcode}</td>
          <td>${callNumber}</td>
          <td>${itemStatus}
          <td>${item.title}</td>
        </tr>
        `);
      }
  }

  function printItemsTableHeader() {
    document.querySelector("#items_table thead").insertAdjacentHTML("beforeend", `
      <tr>
        <th>Barcode</th>
        <th>Call Number</th>
        <th>Item<br/>Status</th>
        <th>Title</th>
      </tr>
      `);
  }
  
}
