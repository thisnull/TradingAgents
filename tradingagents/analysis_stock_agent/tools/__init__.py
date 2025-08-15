"""
数据工具模块
提供A股数据API和MCP服务集成
"""

from .ashare_toolkit import (
    AShareToolkit,
    AShareAPIError,
    create_ashare_toolkit
)

from .mcp_integration import (
    MCPToolkit,
    MCPError,
    create_mcp_toolkit,
    UnifiedDataToolkit
)

__all__ = [
    # A股API工具
    "AShareToolkit",
    "AShareAPIError", 
    "create_ashare_toolkit",
    
    # MCP工具
    "MCPToolkit",
    "MCPError",
    "create_mcp_toolkit",
    
    # 统一工具
    "UnifiedDataToolkit"
]