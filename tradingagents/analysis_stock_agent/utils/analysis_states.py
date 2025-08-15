"""
A股分析系统状态管理
定义系统中使用的所有状态结构和数据模型
"""
from typing import Annotated, Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class InvestmentRecommendation(str, Enum):
    """投资建议枚举"""
    STRONG_BUY = "强烈推荐"
    BUY = "推荐" 
    HOLD = "中性"
    SELL = "不推荐"
    STRONG_SELL = "强烈不推荐"

class AnalysisStatus(str, Enum):
    """分析状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DataSource(BaseModel):
    """数据来源信息"""
    name: str = Field(..., description="数据源名称")
    endpoint: str = Field(..., description="数据端点")
    timestamp: datetime = Field(default_factory=datetime.now, description="数据获取时间")
    version: Optional[str] = Field(None, description="数据版本")

class FinancialAnalysisResult(BaseModel):
    """财务分析结果"""
    # 营收与净利润分析
    revenue_current: Optional[float] = Field(None, description="当前营收(万元)")
    revenue_growth_rate: Optional[float] = Field(None, description="营收增长率(%)")
    revenue_growth_trend: Optional[str] = Field(None, description="营收增长趋势")
    
    profit_current: Optional[float] = Field(None, description="当前净利润(万元)")
    profit_growth_rate: Optional[float] = Field(None, description="净利润增长率(%)")
    profit_growth_trend: Optional[str] = Field(None, description="净利润增长趋势")
    
    # ROE分析
    roe_current: Optional[float] = Field(None, description="当前ROE(%)")
    roe_industry_avg: Optional[float] = Field(None, description="行业平均ROE(%)")
    roe_health_level: Optional[str] = Field(None, description="ROE健康水平")
    roe_trend: Optional[str] = Field(None, description="ROE变化趋势")
    
    # 资产负债表分析
    debt_ratio: Optional[float] = Field(None, description="资产负债率(%)")
    current_ratio: Optional[float] = Field(None, description="流动比率")
    quick_ratio: Optional[float] = Field(None, description="速动比率")
    asset_structure_health: Optional[str] = Field(None, description="资产结构健康度")
    
    # 现金流分析
    operating_cash_flow: Optional[float] = Field(None, description="经营性现金流(万元)")
    cash_flow_profit_ratio: Optional[float] = Field(None, description="现金流/净利润比")
    cash_flow_health: Optional[str] = Field(None, description="现金流健康度")
    
    # 股东回报分析
    dividend_yield: Optional[float] = Field(None, description="股息率(%)")
    avg_dividend_rate: Optional[float] = Field(None, description="近3年平均分红率(%)")
    dividend_stability: Optional[str] = Field(None, description="分红稳定性")
    shareholder_return_rating: Optional[str] = Field(None, description="股东回报评级")
    
    # 综合评分
    financial_score: Optional[float] = Field(None, ge=0, le=10, description="财务健康综合评分")
    key_insights: List[str] = Field(default_factory=list, description="关键洞察")
    risk_warnings: List[str] = Field(default_factory=list, description="风险提示")

class IndustryAnalysisResult(BaseModel):
    """行业分析结果"""
    # 行业基本信息
    industry_name: Optional[str] = Field(None, description="所属行业")
    industry_code: Optional[str] = Field(None, description="行业代码")
    industry_growth_rate: Optional[float] = Field(None, description="行业增长率(%)")
    industry_stage: Optional[str] = Field(None, description="行业发展阶段")
    
    # 行业对比分析
    market_position: Optional[int] = Field(None, description="行业排名")
    market_share: Optional[float] = Field(None, description="市场份额(%)")
    peer_comparison: Dict[str, Any] = Field(default_factory=dict, description="同业对比数据")
    
    # 关键指标对比
    gross_margin_vs_industry: Optional[Dict[str, float]] = Field(None, description="毛利率对比")
    net_margin_vs_industry: Optional[Dict[str, float]] = Field(None, description="净利率对比")
    roe_vs_industry: Optional[Dict[str, float]] = Field(None, description="ROE对比")
    
    # 竞争优势分析
    competitive_advantages: List[str] = Field(default_factory=list, description="竞争优势")
    competitive_disadvantages: List[str] = Field(default_factory=list, description="竞争劣势")
    moat_analysis: Optional[str] = Field(None, description="护城河分析")
    
    # 综合评估
    competition_score: Optional[float] = Field(None, ge=0, le=10, description="竞争力评分")
    industry_outlook: Optional[str] = Field(None, description="行业前景")
    key_competitors: List[str] = Field(default_factory=list, description="主要竞争对手")

class ValuationAnalysisResult(BaseModel):
    """估值分析结果"""
    # 基础估值指标
    current_pe: Optional[float] = Field(None, description="当前PE")
    current_pb: Optional[float] = Field(None, description="当前PB")
    current_ps: Optional[float] = Field(None, description="当前PS")
    
    # PR估值模型
    pr_ratio: Optional[float] = Field(None, description="PR值(PE/ROE)")
    pr_historical_avg: Optional[float] = Field(None, description="历史PR均值")
    valuation_level: Optional[str] = Field(None, description="估值水平")
    
    # 股权变动分析
    ownership_changes: List[Dict[str, Any]] = Field(default_factory=list, description="股权变动记录")
    major_shareholder_changes: Optional[bool] = Field(None, description="大股东是否有变动")
    ownership_risk_level: Optional[str] = Field(None, description="股权风险等级")
    
    # 股东结构分析
    top_shareholder_ratio: Optional[float] = Field(None, description="第一大股东持股比例(%)")
    top10_shareholder_ratio: Optional[float] = Field(None, description="前十大股东持股比例(%)")
    institutional_ratio: Optional[float] = Field(None, description="机构投资者持股比例(%)")
    ownership_concentration: Optional[str] = Field(None, description="股权集中度")
    
    # 技术指标分析
    technical_signals: Dict[str, str] = Field(default_factory=dict, description="技术指标信号")
    price_trend: Optional[str] = Field(None, description="价格趋势")
    volume_analysis: Optional[str] = Field(None, description="成交量分析")
    
    # 市场信号
    market_sentiment: Optional[str] = Field(None, description="市场情绪")
    analyst_consensus: Optional[str] = Field(None, description="分析师一致预期")
    
    # 综合评分
    valuation_score: Optional[float] = Field(None, ge=0, le=10, description="估值合理性评分")
    investment_timing: Optional[str] = Field(None, description="投资时机评估")

class AnalysisResult(BaseModel):
    """完整的分析结果"""
    # 基础信息
    stock_symbol: str = Field(..., description="股票代码")
    company_name: Optional[str] = Field(None, description="公司名称")
    analysis_date: datetime = Field(default_factory=datetime.now, description="分析日期")
    request_id: str = Field(..., description="请求唯一标识")
    
    # 分析结果
    financial_analysis: Optional[FinancialAnalysisResult] = None
    industry_analysis: Optional[IndustryAnalysisResult] = None
    valuation_analysis: Optional[ValuationAnalysisResult] = None
    
    # 综合评分
    financial_score: Optional[float] = Field(None, ge=0, le=10)
    competition_score: Optional[float] = Field(None, ge=0, le=10)
    valuation_score: Optional[float] = Field(None, ge=0, le=10)
    comprehensive_score: Optional[float] = Field(None, ge=0, le=10)
    
    # 最终输出
    final_report: Optional[str] = Field(None, description="完整分析报告")
    investment_recommendation: Optional[InvestmentRecommendation] = None
    target_price: Optional[float] = Field(None, gt=0, description="目标价格")
    confidence_level: Optional[float] = Field(None, ge=0, le=1, description="结论置信度")
    
    # 元数据
    data_sources: List[DataSource] = Field(default_factory=list)
    processing_time: Optional[float] = Field(None, description="处理时间(秒)")
    analysis_status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    
    # 错误和警告
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    @validator('stock_symbol')
    def validate_stock_symbol(cls, v):
        """验证股票代码格式"""
        import re
        if not re.match(r'^[0-9]{6}$', v):
            raise ValueError('股票代码必须是6位数字')
        return v

class AnalysisState(BaseModel):
    """分析过程状态管理"""
    # 基础信息
    stock_symbol: str = Field(..., description="股票代码")
    company_name: Optional[str] = Field(None, description="公司名称")
    analysis_date: datetime = Field(default_factory=datetime.now)
    request_id: str = Field(..., description="请求唯一标识")
    
    # 原始数据存储
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="原始数据")
    processed_data: Dict[str, Any] = Field(default_factory=dict, description="处理后数据")
    
    # Agent执行状态
    financial_analysis_status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    industry_analysis_status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    valuation_analysis_status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    integration_status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    
    # 分析结果
    financial_analysis: Optional[FinancialAnalysisResult] = None
    industry_analysis: Optional[IndustryAnalysisResult] = None
    valuation_analysis: Optional[ValuationAnalysisResult] = None
    
    # 评分结果
    financial_score: Optional[float] = Field(None, ge=0, le=10)
    competition_score: Optional[float] = Field(None, ge=0, le=10)
    valuation_score: Optional[float] = Field(None, ge=0, le=10)
    comprehensive_score: Optional[float] = Field(None, ge=0, le=10)
    
    # 最终输出
    final_report: Optional[str] = None
    investment_recommendation: Optional[InvestmentRecommendation] = None
    target_price: Optional[float] = Field(None, gt=0)
    
    # 元数据
    data_sources: List[DataSource] = Field(default_factory=list)
    processing_time: Optional[float] = None
    current_step: str = Field(default="初始化")
    progress_percentage: float = Field(default=0.0, ge=0, le=100)
    
    # 错误处理
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    retry_count: int = Field(default=0)
    
    # 配置信息
    config: Dict[str, Any] = Field(default_factory=dict)
    
    def add_error(self, error: str):
        """添加错误信息"""
        self.errors.append(f"[{datetime.now().isoformat()}] {error}")
    
    def add_warning(self, warning: str):
        """添加警告信息"""
        self.warnings.append(f"[{datetime.now().isoformat()}] {warning}")
    
    def add_data_source(self, name: str, endpoint: str, version: str = None):
        """添加数据源信息"""
        source = DataSource(
            name=name,
            endpoint=endpoint,
            version=version
        )
        self.data_sources.append(source)
    
    def update_progress(self, step: str, percentage: float):
        """更新进度信息"""
        self.current_step = step
        self.progress_percentage = min(100.0, max(0.0, percentage))
    
    def to_result(self) -> AnalysisResult:
        """转换为最终结果"""
        return AnalysisResult(
            stock_symbol=self.stock_symbol,
            company_name=self.company_name,
            analysis_date=self.analysis_date,
            request_id=self.request_id,
            financial_analysis=self.financial_analysis,
            industry_analysis=self.industry_analysis,
            valuation_analysis=self.valuation_analysis,
            financial_score=self.financial_score,
            competition_score=self.competition_score,
            valuation_score=self.valuation_score,
            comprehensive_score=self.comprehensive_score,
            final_report=self.final_report,
            investment_recommendation=self.investment_recommendation,
            target_price=self.target_price,
            data_sources=self.data_sources,
            processing_time=self.processing_time,
            analysis_status=AnalysisStatus.COMPLETED if not self.errors else AnalysisStatus.FAILED,
            errors=self.errors,
            warnings=self.warnings
        )
    
    class Config:
        arbitrary_types_allowed = True

# 工具函数
def create_analysis_state(symbol: str, request_id: str = None, config: Dict[str, Any] = None) -> AnalysisState:
    """创建新的分析状态"""
    import uuid
    
    if request_id is None:
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    return AnalysisState(
        stock_symbol=symbol,
        request_id=request_id,
        config=config or {}
    )