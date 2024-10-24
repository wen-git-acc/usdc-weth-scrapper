from typing import Tuple

from app.routes.deposit_route.models import DepositDetail, DepositPlan, DistributedFundResult, PortfolioDetails


def get_distribute_funds_with_valid_data_test_cases() -> (
    list[Tuple[list[DepositPlan], list[DepositDetail], DistributedFundResult]]
):
    return (
        [
           (
                [
                DepositPlan(
                    plan_name="one-time",
                    portfolio_details=[
                        PortfolioDetails(
                            portfolio_name="High risk",
                            amount=10000.00
                        ),
                        PortfolioDetails(
                            portfolio_name="Retirement",
                            amount=500.0
                        ),
                    ]
                ),
                DepositPlan(
                    plan_name="monthly",
                    portfolio_details=[
                        PortfolioDetails(
                            portfolio_name="High risk",
                            amount=0.00
                        ),
                        PortfolioDetails(
                            portfolio_name="Retirement",
                            amount=100.00
                        ),
                    ]
                ),

            ],
            [
                DepositDetail(
                    reference_code="123",
                    amount=10500.00
                ),
                DepositDetail(
                    reference_code="123",
                    amount=100.0
                ),
            ],
            DistributedFundResult(
                total_amount=10600.00,
                reference_code="123",
                portfolio_distribution=[
                    PortfolioDetails(
                        portfolio_name="High risk",
                        amount=10000.00
                    ),
                    PortfolioDetails(
                        portfolio_name="Retirement",
                        amount=600.00
                    ),
                ],
            ) 
        
           )
        ]
    )

def get_distribute_funds_with_multiple_deposit_plan_test_cases() -> (
    list[Tuple[list[DepositPlan], list[DepositDetail], str]]
):
    return (
        [
           (
                [
                DepositPlan(
                    plan_name="one-time",
                    portfolio_details=[
                        PortfolioDetails(
                            portfolio_name="High risk",
                            amount=10000.00
                        ),
                        PortfolioDetails(
                            portfolio_name="Retirement",
                            amount=500.0
                        ),
                    ]
                ),
                DepositPlan(
                    plan_name="monthly",
                    portfolio_details=[
                        PortfolioDetails(
                            portfolio_name="High risk",
                            amount=0.00
                        ),
                        PortfolioDetails(
                            portfolio_name="Retirement",
                            amount=100.00
                        ),
                    ]
                ),
                DepositPlan(
                    plan_name="monthly",
                    portfolio_details=[
                        PortfolioDetails(
                            portfolio_name="High risk",
                            amount=0.00
                        ),
                        PortfolioDetails(
                            portfolio_name="Retirement",
                            amount=100.00
                        ),
                    ]
                ),               
            ],
            [
                DepositDetail(
                    reference_code="123",
                    amount=10500.00
                ),
                DepositDetail(
                    reference_code="123",
                    amount=100.0
                ),
            ],
            "Deposit plan is more than 2"
           )
        ]
    )