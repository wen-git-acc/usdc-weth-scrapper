from app.core.fund_allocator.model import DepositPlanDetail
from app.core.helper.client import HelperClient
from app.routes.deposit_route.models import PortfolioDetails


helper_client = HelperClient()

def test_get_portfolio_detail_from_plan():
    portfolio_details = [
        PortfolioDetails(portfolio_name="portfolio1", amount=1000.00),
        PortfolioDetails(portfolio_name="portfolio2", amount=2000.00),
        PortfolioDetails(portfolio_name="portfolio3", amount=3000.00),
    ]

    portfolio_distribution_map = {
        "portfolio1": 0.00,
        "portfolio2": 0.00,
        "portfolio3": 0.00,
    }

    expected_portfolio_distribution_map = {
        "portfolio1": 0.00,
        "portfolio2": 0.00,
        "portfolio3": 0.00,
    }

    expected_result = DepositPlanDetail(
        portfolio_names=["portfolio1", "portfolio2", "portfolio3"],
        total_amount=6000.00,
        individual_amount=[1000.00, 2000.00, 3000.00]
    )

    result = helper_client.get_portfolio_detail_from_plan(
        portfolio_details=portfolio_details, 
        portfolio_distribution_map=portfolio_distribution_map
        )

    assert expected_result.total_amount == result.total_amount
    
    for index, value in enumerate(expected_result.individual_amount):
        assert value == result.individual_amount[index]

    for index, value in enumerate(expected_result.portfolio_names):
        assert value == result.portfolio_names[index]

    for name, value in expected_portfolio_distribution_map.items():
        assert portfolio_distribution_map[name] == value
