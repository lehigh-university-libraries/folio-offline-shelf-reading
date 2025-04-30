import smtplib
from email.message import EmailMessage

class Reporter:
  """ Send results summary to email recipients. """

  def __init__(self, config):
    self._smtp_host = config.get("Email", "smtp_host")
    self._from_address = config.get("Email", "from_address")
    self._from_name = config.get("Email", "from_name")
    self._to_address = config.get("Email", "to_address")

  def report_results(self, results: dict):
    message_body = ''

    unknown_barcodes = results['unknownBarcodes']
    message_body += '\n\nUnknown Barcodes:'
    for barcode in unknown_barcodes:
       message_body += f'\n{barcode}'

    items_input = results['itemsInput']
    items_by_condition = self._group_by(items_input, 'shelf_condition')
    message_body += self._format_section('Shelf Condition', items_by_condition)

    items_by_item_status = self._group_by(items_input, 'item_status', 'Already inventoried')
    message_body += self._format_section(
       'Item Status (excluding Available, or already inventoried items)', 
       items_by_item_status
    )

    subject = f'FOLIO Offline Shelf Reading report'

    with smtplib.SMTP(self._smtp_host) as server:
        msg = EmailMessage()
        msg.set_content(message_body)
        msg['Subject'] = subject
        msg['From'] = f"{self._from_name} <{self._from_address}>" if self._from_name else self._from_address
        msg['To'] = self._to_address

        server.send_message(msg)

  def _group_by(self, items, prop, skip_text = None):
    grouped_data = {}
    for item in items:
      value = item.get(prop)
      if not value or (skip_text and skip_text in value): 
        continue
      if value not in grouped_data:
        grouped_data[value] = []
        grouped_data[value].append(item)
    return grouped_data

  def _format_section(self, heading, results):
    message = f'\n\n-----\n\n{heading}'
    for value, items in results.items():
      message += f'\n\n{value}'
      for item in items:
          message += f'\n{self._format_item(item)}'
    return message

  def _format_item(self, item):
    return str(item)

  def _format_results_message(self, results, heading):
    message = ""
    if len(results):
        message += f"\n\n{heading}:"
        for result in results:
            message += f"\n- {result}"
    return message
