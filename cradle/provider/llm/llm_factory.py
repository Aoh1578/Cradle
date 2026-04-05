from cradle.provider.llm.openai import OpenAIProvider
from cradle.provider.llm.restful_claude import RestfulClaudeProvider
from cradle.utils import Singleton
from cradle.utils.json_utils import load_json
from cradle.utils.file_utils import assemble_project_path


class LLMFactory(metaclass=Singleton):

    def __init__(self):
        self._builders = {}


    def _detect_provider_type(self, config_path):
        """Detect provider type from config content or fall back to filename matching."""
        try:
            if isinstance(config_path, dict):
                conf = config_path
            else:
                path = assemble_project_path(config_path)
                conf = load_json(path)

            provider_type = conf.get("provider_type", None)
            if provider_type:
                return provider_type
        except Exception:
            pass

        # Fallback: filename-based routing for backward compatibility
        key = config_path if isinstance(config_path, str) else ""
        if "claude" in key:
            return "claude"
        if "openai" in key:
            return "openai"
        return "openai"


    def create(self, llm_provider_config_path, embed_provider_config_path, **kwargs):

        llm_provider = None
        embed_provider = None

        provider_type = self._detect_provider_type(llm_provider_config_path)

        if provider_type in ("openai", "openai_compat"):
            llm_provider = OpenAIProvider()
            llm_provider.init_provider(llm_provider_config_path)
            embed_provider = llm_provider
        elif provider_type == "claude":
            llm_provider = RestfulClaudeProvider()
            llm_provider.init_provider(llm_provider_config_path)
            embed_provider = OpenAIProvider()
            embed_provider.init_provider(embed_provider_config_path)

        if not llm_provider or not embed_provider:
            raise ValueError(f"Unknown provider_type: {provider_type} from {llm_provider_config_path}")

        return llm_provider, embed_provider
