# def user_pre_save(sender, instance, **kwargs):
#     user = sender.objects.get(pk=instance.pk)
#     if instance.email != user.email:
#         instance.approve_email = False
#     if instance.phone != user.phone:
#         instance.approve_phone = False
