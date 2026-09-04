from typing import Optional
from backend.app.core.config import settings

class IncoisErddapBuilder:
    """
    Constructs standardized spatial-temporal ERDDAP tabledap/griddap query URLs for INCOIS.
    Targets coastal Maharashtra bounding box by default.
    """
    def __init__(self, base_url: str = settings.INCOIS_ERDDAP_URL):
        self.base_url = base_url.rstrip('/')

    def build_griddap_url(
        self,
        dataset_id: str,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        variables: list[str]
    ) -> str:
        var_query = ",".join(variables)
        return (
            f"{self.base_url}/griddap/{dataset_id}.json"
            f"?{var_query}[({min_lat}):1:({max_lat})][({min_lon}):1:({max_lon})]"
        )

    def build_tabledap_url(
        self,
        dataset_id: str,
        parameters: list[str],
        time_start: Optional[str] = None
    ) -> str:
        param_query = ",".join(parameters)
        url = f"{self.base_url}/tabledap/{dataset_id}.json?{param_query}"
        if time_start:
            url += f"&time>={time_start}"
        return url
