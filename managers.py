class MessageManager(models.Manager):
   def get_queryset(self):
       return super().get_queryset().filter(is_removed=False)

   def inbox(self, user):
       """
       Returns all messages that were received
       by the given user
       """
       EDIT = 0
       SENDING_IS_SCHEDULED = 1
       status = [EDIT, SENDING_IS_SCHEDULED]
       return self.filter(
           Q(recipient_account=user, recipient_deleted_at__isnull=True, new=user) |
           Q(sent_copy=True, sender=user, copy_deleted_at__isnull=True, new=user))\
           .exclude(status__in=status)\
           .annotate(new_message=ExpressionWrapper(Q(newmessages__read_at__isnull=True),
                                                   output_field=BooleanField()))\
           .order_by('-new_message', '-delivery_date')

   def sent(self, user):
       """
       Returns all messages sent by this user,
       exclude those in the draft
       """
       return self.filter(
           sender=user,
           sender_deleted_at__isnull=True,
       ).exclude(status=0).order_by('-delivery_date')

   def draft(self, user):
       """
       Returns all user messages in the draft.
       """
       return self.filter(
           sender=user,
           status=0
       ).order_by('-created')
