class InboxMessageView(viewsets.ReadOnlyModelViewSet, mixins.DestroyModelMixin):
   permission_classes = (IsAuthenticated,)
   serializer_class = MessageSerializer
   queryset = Message.objects.all()

   def get_queryset(self):
       user = self.request.user
       return Message.objects.inbox(user=user).select_related('sender', 'recipient_account')\
           .prefetch_related('attachments')

   def perform_destroy(self, instance):
       # Add the date the copy message was deleted
       if instance.sent_copy and instance.sender == self.request.user:
           instance.copy_deleted_at = datetime.now()
           instance.save()
           silence_send_notification.delay(badge=instance.sender.inbox_count,
                                           user_id=instance.sender.pk)
       else:
           # Add the date the message was deleted for the recipient
           instance.recipient_deleted_at = datetime.now()
           instance.save()
           silence_send_notification.delay(badge=instance.recipient_account.inbox_count,
                                           user_id=instance.recipient_account.pk)

   def retrieve(self, request, *args, **kwargs):
       instance = self.get_object()
       # Get the object of a new message, if the field read_at empty add the date of reading
       user_massage = NewMessages.objects.get(user=self.request.user, message=instance)

       if instance.recipient_account == request.user and user_massage.read_at is None:
           instance.status = 3
           instance.save()
       if user_massage.read_at is None:
           user_massage.read_at = datetime.now()
           user_massage.save()
           silence_send_notification.delay(
               badge=instance.recipient_account.inbox_count,
               user_id=instance.recipient_account.pk
           )
       # When the recipient goes into the message, change the status to read
       serializer = self.get_serializer(instance)
       return Response(serializer.data)
