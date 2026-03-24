import os
import pytest
from mouseai.core.ai_sync import AISync


def test_aisync_missing_keys():
    os.environ.pop('OPENAI_API_KEY', None)
    os.environ.pop('SERPAPI_API_KEY', None)

    sync = AISync()
    with pytest.raises(ValueError):
        sync.sync_data('mouse sensitivity gaming')
