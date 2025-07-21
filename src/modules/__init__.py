from .schema_agent import SchemaAgent
from .extraction_agent import ExtractionAgent
from .reflection_agent import ReflectionAgent

# Optional import for CaseRepositoryHandler
try:
    from .knowledge_base import CaseRepositoryHandler
except ImportError as e:
    print(f"Note: CaseRepositoryHandler not available: {e}")
    CaseRepositoryHandler = None

# Export all classes
__all__ = ['SchemaAgent', 'ExtractionAgent', 'ReflectionAgent', 'CaseRepositoryHandler']
