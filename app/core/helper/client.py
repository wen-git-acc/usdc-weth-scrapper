from decimal import Decimal
from app.core.fund_allocator.model import DepositPlanDetail
from app.routes.deposit_route.models import PortfolioDetails

class HelperClient:

    def __init__(self) -> None:
        pass

    def get_portfolio_detail_from_plan(self, portfolio_details: list[PortfolioDetails], portfolio_distribution_map: dict[str, Decimal]) -> DepositPlanDetail:
        result = DepositPlanDetail()

        for portfolio in portfolio_details:
            if portfolio.amount >= 0:
                result.portfolio_names.append(portfolio.portfolio_name)
                result.individual_amount.append(Decimal(str(portfolio.amount)))
                portfolio_distribution_map[portfolio.portfolio_name] = Decimal(str(0.00))

        result.total_amount = sum(result.individual_amount) 

        return result
