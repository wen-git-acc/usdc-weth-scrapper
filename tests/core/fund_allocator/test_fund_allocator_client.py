from decimal import Decimal

import pytest
from app.core.dependencies import get_fund_allocator_client
from app.core.fund_allocator.model import DepositPlanDetail
from app.routes.deposit_route.models import DepositDetail, DepositPlan, DistributedFundResult
from tests.core.fund_allocator.fund_allocator_test_cases import get_distribute_funds_with_multiple_deposit_plan_test_cases, get_distribute_funds_with_valid_data_test_cases


def test_distribute_funds_by_ratio():
    fund_allocator_client = get_fund_allocator_client()
    deposit_amount: Decimal = Decimal('1000.00')
    plan_details = DepositPlanDetail(
        portfolio_names=["portfolio1", "portfolio2", "portfolio3"],
        total_amount=Decimal('1000.00'),
        individual_amount=[Decimal('500.00'), Decimal('300.00'), Decimal('200.00')],
    )
    portfolio_distribution_map = {
        "portfolio1": Decimal('0.00'),
        "portfolio2": Decimal('0.00'),
        "portfolio3": Decimal('0.00'),
    }

    expected_portfolio_distribution_map = {
        "portfolio1": Decimal('500.00'),
        "portfolio2": Decimal('300.00'),
        "portfolio3": Decimal('200.00'),
    }
    fund_allocator_client.distribute_funds_by_ratio(plan_details, deposit_amount, portfolio_distribution_map)

    for name, value in expected_portfolio_distribution_map.items():
        assert portfolio_distribution_map[name] == value

def test_distribute_funds_by_ratio_zero_amount():
    fund_allocator_client = get_fund_allocator_client()
    deposit_amount: Decimal = Decimal('0.00')
    plan_details = DepositPlanDetail(
        portfolio_names=["portfolio1", "portfolio2", "portfolio3"],
        total_amount=Decimal('1000.00'),
        individual_amount=[Decimal('500.00'), Decimal('300.00'), Decimal('200.00')],
    )

    portfolio_distribution_map = {
        "portfolio1": Decimal('0.00'),
        "portfolio2": Decimal('0.00'),
        "portfolio3": Decimal('0.00'),
    }

    expected_portfolio_distribution_map = {
        "portfolio1": Decimal('0.00'),
        "portfolio2": Decimal('0.00'),
        "portfolio3": Decimal('0.00'),
    }
    
    fund_allocator_client.distribute_funds_by_ratio(plan_details, deposit_amount, portfolio_distribution_map)

    for name, value in expected_portfolio_distribution_map.items():
        assert portfolio_distribution_map[name] == value


def test_distribute_funds_with_one_time_plan_with_ratio():
    fund_allocator_client = get_fund_allocator_client()
    deposit_amount: Decimal = Decimal('1000.00')
    plan_details = DepositPlanDetail(
        portfolio_names=["portfolio1", "portfolio2", "portfolio3"],
        total_amount=Decimal('1000.00'),
        individual_amount=[Decimal('500.00'), Decimal('300.00'), Decimal('200.00')],
    )

    portfolio_distribution_map = {
        "portfolio1": Decimal('0.00'),
        "portfolio2": Decimal('0.00'),
        "portfolio3": Decimal('0.00'),
    }

    expected_portfolio_distribution_map = {
        "portfolio1": Decimal('500.00'),
        "portfolio2": Decimal('300.00'),
        "portfolio3": Decimal('200.00'),
    }
    
    fund_allocator_client.one_time_plan_distribution(plan_details, deposit_amount, False ,portfolio_distribution_map)

    for name, value in expected_portfolio_distribution_map.items():
        assert portfolio_distribution_map[name] == value

def test_distribute_funds_with_one_time_plan_without_ratio():
    fund_allocator_client = get_fund_allocator_client()
    deposit_amount: Decimal = Decimal('1000.00')
    plan_details = DepositPlanDetail(
        portfolio_names=["portfolio1", "portfolio2", "portfolio3"],
        total_amount=Decimal('1000.00'),
        individual_amount=[Decimal('500.00'), Decimal('300.00'), Decimal('200.00')],
    )

    portfolio_distribution_map = {
        "portfolio1": Decimal('0.00'),
        "portfolio2": Decimal('0.00'),
        "portfolio3": Decimal('0.00'),
    }

    expected_portfolio_distribution_map = {
        "portfolio1": Decimal('500.00'),
        "portfolio2": Decimal('300.00'),
        "portfolio3": Decimal('200.00'),
    }
    
    remaining_amount = fund_allocator_client.one_time_plan_distribution(plan_details, deposit_amount, False ,portfolio_distribution_map)

    for name, value in expected_portfolio_distribution_map.items():
        assert portfolio_distribution_map[name] == value
    
    assert remaining_amount == Decimal('0.00')

def test_distribute_funds_with_one_time_plan_without_ratio_with_extra_amount():
    fund_allocator_client = get_fund_allocator_client()
    deposit_amount: Decimal = Decimal('1200.00')
    plan_details = DepositPlanDetail(
        portfolio_names=["portfolio1", "portfolio2", "portfolio3"],
        total_amount=Decimal('1000.00'),
        individual_amount=[Decimal('500.00'), Decimal('300.00'), Decimal('200.00')],
    )

    portfolio_distribution_map = {
        "portfolio1": Decimal('0.00'),
        "portfolio2": Decimal('0.00'),
        "portfolio3": Decimal('0.00'),
    }

    expected_portfolio_distribution_map = {
        "portfolio1": Decimal('500.00'),
        "portfolio2": Decimal('300.00'),
        "portfolio3": Decimal('200.00'),
    }
    remaining_amount = fund_allocator_client.one_time_plan_distribution(plan_details, deposit_amount, True ,portfolio_distribution_map)

    for name, value in expected_portfolio_distribution_map.items():
        assert portfolio_distribution_map[name] == value
    
    assert remaining_amount == Decimal('200.00')


@pytest.mark.parametrize("deposit_plans, deposit_details, expected_result", get_distribute_funds_with_valid_data_test_cases())
def test_distribute_funds_with_valid_data(
    deposit_plans:list[DepositPlan], deposit_details:list[DepositDetail], expected_result: DistributedFundResult
) -> None:
    fund_allocator_client = get_fund_allocator_client()
    actual_result = fund_allocator_client.distribute_funds(deposit_plans, deposit_details)

    assert actual_result.total_amount == expected_result.total_amount
    assert actual_result.reference_code == expected_result.reference_code
    assert actual_result.portfolio_distribution[0].portfolio_name == expected_result.portfolio_distribution[0].portfolio_name   
    assert actual_result.portfolio_distribution[0].amount == expected_result.portfolio_distribution[0].amount
    assert actual_result.portfolio_distribution[1].portfolio_name == expected_result.portfolio_distribution[1].portfolio_name
    assert actual_result.portfolio_distribution[1].amount == expected_result.portfolio_distribution[1].amount


@pytest.mark.parametrize("deposit_plans, deposit_details, expected_result", get_distribute_funds_with_multiple_deposit_plan_test_cases())
def test_distribute_funds_with_duplicate_plan_data(
    deposit_plans:list[DepositPlan], deposit_details:list[DepositDetail], expected_result: str
) -> None:
    fund_allocator_client = get_fund_allocator_client()

    with pytest.raises(Exception) as excinfo:
        fund_allocator_client.distribute_funds(deposit_plans, deposit_details)

    assert expected_result in str(excinfo.value)
