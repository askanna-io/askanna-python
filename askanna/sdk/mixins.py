from typing import Optional

__all__ = [
    "ListMixin",
]


class ListMixin:
    """Base class for list method

    This class contains the list method, which is used by all SDKs that have a list method. The list method contains
    logic to get all results from the API, even if the number of results is higher than the page size.

    To use this class, you need to set the gateway attribute to the gateway class

    Example:

        class WorkspaceSDK(ListMixin):
            gateway = WorkspaceGateway()
    """

    gateway = None

    def __init__(self):
        self.list_total_count = None

    def get_gateway(self):
        assert self.gateway is not None, "Gateway is not set"
        return self.gateway

    def list(
        self,
        number_of_results: int = 100,
        order_by: Optional[str] = None,
        other_query_params: Optional[dict] = None,
    ) -> list:
        gateway = self.get_gateway()
        query_params = {
            "page_size": number_of_results,
            "order_by": order_by,
        }
        if other_query_params:
            assert isinstance(other_query_params, dict), "other_query_params must be a dict"
            query_params.update(other_query_params)

        list_response = gateway.list(**query_params)
        results = list_response.results

        self.list_total_count = list_response.total_count
        if number_of_results > len(results):
            while list_response.next_url is not None and len(results) < number_of_results:
                list_response = gateway.list(
                    cursor=list_response.next_url_cursor,
                    **query_params,
                )
                results.extend(list_response.results)

        return results[:number_of_results]
