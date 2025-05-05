--metadb:function get_items_between_barcodes

DROP FUNCTION IF EXISTS get_items_between_barcodes;

CREATE FUNCTION get_items_between_barcodes(
    start_barcode TEXT,
    end_barcode TEXT
)
RETURNS TABLE (
    barcode TEXT,
    id UUID,
    effective_shelving_order TEXT,
    item_call_number TEXT,
    holdings_call_number TEXT,
    item_status TEXT,
    statistical_codes TEXT,
    title TEXT
)
AS
$$
WITH 
	bookends AS (
		SELECT 
	        *, 
	        row_number() OVER (
				ORDER BY effective_shelving_order
					COLLATE ucs_basic
			) AS row_num 
	    FROM folio_inventory.item__t
		WHERE barcode IN (start_barcode, end_barcode)
	),
	statistical_codes AS (
		SELECT item.id, jsonb_extract_path_text(item_raw.jsonb, 'statisticalCodeIds') AS codes
		FROM folio_inventory.item__t item
		LEFT JOIN folio_inventory.item item_raw
			ON item.id = item_raw.id
	)

SELECT 
	item.barcode, 
	item.id,
	item.effective_shelving_order, 
	item.item_level_call_number AS item_call_number, 
	holdings.call_number AS holdings_call_number, 
	jsonb_extract_path_text(item_raw.jsonb, 'status', 'name'),
    statistical_codes.codes as statistical_codes,
	inst.title 
FROM folio_inventory.item__t item
LEFT JOIN folio_inventory.item item_raw
	ON item.id = item_raw.id
LEFT JOIN folio_inventory.holdings_record__t holdings 
    ON item.holdings_record_id = holdings.id
LEFT JOIN folio_inventory.instance__t inst 
    ON holdings.instance_id = inst.id
LEFT JOIN statistical_codes 
	ON item.id = statistical_codes.id
WHERE item.effective_location_id IN 
    (SELECT effective_location_id FROM bookends WHERE row_num = 1)
AND item.effective_location_id IN 
    (SELECT effective_location_id FROM bookends WHERE row_num = 2)
AND item.effective_shelving_order >= 
    (SELECT effective_shelving_order FROM bookends WHERE row_num = 1)
	COLLATE ucs_basic
AND item.effective_shelving_order <= 
    (SELECT effective_shelving_order FROM bookends WHERE row_num = 2)
	COLLATE ucs_basic
AND not item.discovery_suppress
ORDER BY item.effective_shelving_order
	COLLATE ucs_basic
$$
LANGUAGE SQL;
