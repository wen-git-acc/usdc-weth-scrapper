from typing import Tuple

from fastapi.testclient import TestClient
from regex import D
from app.routes.deposit_route.models import DepositDetail, DepositPlan, DepositPlanRequestModel, DepositPlanResponseModel, DistributedFundResult, PortfolioDetails

def get_deposit_plan_mock_test_cases() -> (
    list[Tuple[int, DepositPlanRequestModel]]
):
    return [
        (200, DepositPlanRequestModel()),
    ]

def get_deposit_plan_invalid_base_test_cases() -> (
    list[Tuple[DepositPlanRequestModel, str, int]]
):
    return [
        (
            DepositPlanRequestModel(
                deposit_details=[],
                deposit_plans=[]
            ),
            "Deposit plan or deposit detail is empty.",
            500
        ),
        (
            DepositPlanRequestModel(
                deposit_plans=[
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
                deposit_details=[
                    DepositDetail(
                        reference_code="123",
                        amount=10500.00
                    ),
                    DepositDetail(
                        reference_code="1aa23",
                        amount=100.0
                    ),
                ]
            ),
            "Reference code is not unique",
            500
        ),
        (
            DepositPlanRequestModel(
                deposit_plans=[
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
                deposit_details=[
                    DepositDetail(
                        reference_code="123",
                        amount=10500.00
                    ),
                    DepositDetail(
                        reference_code="123",
                        amount=100.0
                    ),
                ]
            ),
            "Duplicate deposit plan found",
            500
        ),
        (
            DepositPlanRequestModel(
                deposit_plans=[
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
                deposit_details=[
                    DepositDetail(
                        reference_code="123",
                        amount=10500.00
                    ),
                    DepositDetail(
                        reference_code="123",
                        amount=100.0
                    ),
                ]
            ),
            "Deposit plan is more than 2.",
            500
        ),
    ]


def get_deposit_plan_valid_base_test_cases() -> (
    list[Tuple[DepositPlanRequestModel, DepositPlanResponseModel]]
):
    return [
        (
            DepositPlanRequestModel(
                deposit_plans=[
                    DepositPlan(
                        plan_name="monthly",
                        portfolio_details=[
                            PortfolioDetails(
                                portfolio_name="High risk",
                                amount=50.00
                            ),
                            PortfolioDetails(
                                portfolio_name="Retirement",
                                amount=100.00
                            ),
                        ]
                    ),
                ],
                deposit_details=[
                    DepositDetail(
                        reference_code="123",
                        amount=50
                    ),
                    DepositDetail(
                        reference_code="123",
                        amount=100.0
                    ),
                ]
            ),
            DepositPlanResponseModel(
                message="Success",
                error=False,
                details="",
                result=DistributedFundResult(
                    total_amount=150.0,
                    reference_code="123",
                    portfolio_distribution=[
                        PortfolioDetails(
                            portfolio_name="High risk",
                            amount=50.0
                        ),
                        PortfolioDetails(
                            portfolio_name="Retirement",
                            amount=100.00
                        ),
                    ]
                ) 
            )
        ),
        (
            DepositPlanRequestModel(
                deposit_plans=[
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
                            PortfolioDetails(
                                portfolio_name="Portfolio 3",
                                amount=0.0
                            ),
                        ]
                    ),
                ],
                deposit_details=[
                    DepositDetail(
                        reference_code="123",
                        amount=10000.00
                    ),
                    DepositDetail(
                        reference_code="123",
                        amount=500.0
                    ),
                ]
            ),
            DepositPlanResponseModel(
                message="Success",
                error=False,
                details="",
                result=DistributedFundResult(
                    total_amount=10500.0,
                    reference_code="123",
                    portfolio_distribution=[
                        PortfolioDetails(
                            portfolio_name="High risk",
                            amount=10000.0
                        ),
                        PortfolioDetails(
                            portfolio_name="Retirement",
                            amount=500.00
                        ),
                        PortfolioDetails(
                            portfolio_name="Portfolio 3",
                            amount=0.0
                        ),
                    ]
                ) 
            )
        ),
        (
            DepositPlanRequestModel(
                deposit_plans=[
                    DepositPlan(
                        plan_name="one-time",
                        portfolio_details=[
                            PortfolioDetails(
                                portfolio_name="High risk",
                                amount=10.56
                            ),
                            PortfolioDetails(
                                portfolio_name="Retirement",
                                amount=550.00
                            ),
                        ]
                    ),
                    DepositPlan(
                        plan_name="monthly",
                        portfolio_details=[
                            PortfolioDetails(
                                portfolio_name="High risk",
                                amount=10.20
                            ),
                            PortfolioDetails(
                                portfolio_name="Retirement",
                                amount=100.50
                            ),
                        ]
                    ),
                ],
                deposit_details=[
                    DepositDetail(
                        reference_code="123",
                        amount=580.00
                    ),
                    DepositDetail(
                        reference_code="123",
                        amount=100.0
                    ),
                ]
            ),
            DepositPlanResponseModel(
                message="Success",
                error=False,
                details="",
                result=DistributedFundResult(
                    total_amount=680.0,
                    reference_code="123",
                    portfolio_distribution=[
                        PortfolioDetails(
                            portfolio_name="High risk",
                            amount=21.57
                        ),
                        PortfolioDetails(
                            portfolio_name="Retirement",
                            amount=658.43
                        ),
                    ]
                ) 
            )
        ),
    ]