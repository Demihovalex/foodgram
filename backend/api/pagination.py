from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Пагинатор с параметром limit вместо page_size."""
    page_size_query_param = 'limit'
    page_size = 6
