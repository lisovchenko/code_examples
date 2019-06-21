@app.task
def action_storage_capacity(new_size, previous_size, sender_pk):
   # Task to send service message about the fullness of the memory
   BYTES_TO_GB = 0.000000001
   sender = User.objects.get(pk=sender_pk)
   message_query = Message.objects.filter(
       recipient_account=sender.pk,
       recipient_deleted_at__isnull=True,
   )
   new_percent = sender.percent_storage(new_size)
   previous_percent = sender.percent_storage(previous_size)
   residue_storage = sender.total_storage_size - (new_size * BYTES_TO_GB)
   residue_storage = float('%.2f' % residue_storage)

   # if new >= range > previous and new > previous send service message
   percent_ranges = [
       (100, 'Storage_100', SPENT_100_STORAGE),
       (95.0, 'Storage_95', SPENT_95_STORAGE),
       (90.0, 'Storage_90', SPENT_90_STORAGE),
       (85.0, 'Storage_85', SPENT_85_STORAGE),
       (75.0, 'Storage_75', SPENT_75_STORAGE),
       (50.0, 'Storage_50', SPENT_50_STORAGE)
   ]

   for percent, verb, text in percent_ranges:
       if new_percent >= percent > previous_percent and\
               new_percent > previous_percent and not \
               message_query.filter(verb=verb).exists():
           send_service_message(verb=verb, text=text,
                                recipient=sender, format_text=[residue_storage])
  
