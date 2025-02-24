from src.mcp_server_box import box_search_tool
import pytest_asyncio
import pytest


@pytest.mark.asyncio
async def test_mcp_server_search():
    search_results = await box_search_tool("HAB-1")
    assert len(search_results) > 0
