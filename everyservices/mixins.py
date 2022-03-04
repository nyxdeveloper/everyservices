# rest framework
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class ModelOptionFieldsMixin:
    opt = None

    @action(methods=["GET"], detail=False, url_path="opt")
    def get_options(self, *args, **kwargs):
        if self.opt is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            [{f: obj[i] for f, i in zip(self.opt, range(len(self.opt)))} for obj in
             self.get_queryset().values_list(*self.opt)], status=status.HTTP_200_OK
        )
