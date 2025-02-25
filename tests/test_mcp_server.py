from src.mcp_server_box import box_search_tool, box_read_tool
import pytest


@pytest.mark.asyncio
async def test_mcp_server_search():
    search_results = await box_search_tool("HAB-1")
    assert len(search_results) > 0


@pytest.mark.asyncio
async def test_mcp_server_read():
    # HAB-1-01.docx = 1728677291168. This file must exists
    resp = await box_read_tool("1728677291168")

    assert resp is not None
    assert len(resp) > 0
    assert "HAB-1-01" in resp
