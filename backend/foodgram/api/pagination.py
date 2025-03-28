from rest_framework.pagination import PageNumberPagination


class PaginatorWithLimit(PageNumberPagination):

    page_size_query_param = 'limit'
