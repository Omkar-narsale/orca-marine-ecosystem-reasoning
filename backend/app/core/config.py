import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow", case_sensitive=True)

    PROJECT_NAME: str = "ORCA Marine Intelligence API"
    VERSION: str = "3.0.0"
    API_V1_STR: str = "/api"
    
    # Target Operational Bounding Box: Mumbai / Maharashtra Coastal Region
    DEFAULT_MIN_LAT: float = 18.0
    DEFAULT_MAX_LAT: float = 20.0
    DEFAULT_MIN_LON: float = 71.5
    DEFAULT_MAX_LON: float = 73.5
    
    # Official Source Endpoints
    INCOIS_BASE_URL: str = "https://incois.gov.in"
    INCOIS_OSF_URL: str = "https://incois.gov.in/oceanservices/osfforecast.jsp"
    INCOIS_PFZ_URL: str = "https://incois.gov.in/MarineFisheries/PfzAdvisory"
    INCOIS_ERDDAP_URL: str = "https://erddap.incois.gov.in/erddap"
    
    IMD_API_BASE_URL: str = "https://api.imd.gov.in/public"
    IMD_PUBLIC_URL: str = "https://api.imd.gov.in/public/index.php"
    
    MOSDAC_BASE_URL: str = "https://www.mosdac.gov.in"
    MOSDAC_API_DOCS: str = "https://mosdac.gov.in/downloadapi-manual"
    
    GIS_CADASTRE_URL: str = "https://hydro-india.nic.in"
    BHUVAN_API_URL: str = "https://bhuvan-app1.nrsc.gov.in/api"
    BHUVAN_API_TOKEN: Optional[str] = os.getenv("BHUVAN_API_TOKEN", None)
    
    # Timeouts & Cache
    HTTP_TIMEOUT_SECONDS: float = 10.0
    WEATHER_CACHE_TTL_SECONDS: int = 600       # 10 minutes
    OCEAN_FORECAST_CACHE_TTL_SECONDS: int = 1800 # 30 minutes
    STATIC_CACHE_TTL_SECONDS: int = 86400      # 24 hours

    # LLM & Agent Configuration (Groq & Pluggable Providers)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq" if os.getenv("GROQ_API_KEY") else "deterministic_fallback")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY", None)
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", None)
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Agent Guardrails & Loop Protection
    MAX_AGENT_STEPS: int = 8
    MAX_TOOL_CALLS_PER_AGENT: int = 6
    AGENT_TIMEOUT_SECONDS: float = 12.0
    MAX_RETRY_LIMIT: int = 2
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

settings = Settings()
