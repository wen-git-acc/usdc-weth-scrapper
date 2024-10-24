import pytest
from fastapi.testclient import TestClient
from app.routes.deposit_route.models import DepositPlanRequestModel, DepositPlanResponseModel
from app.server import app
from tests.routes.deposit_route.deposit_plan_test_cases import get_deposit_plan_invalid_base_test_cases, get_deposit_plan_valid_base_test_cases, get_deposit_plan_mock_test_cases


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}



def plan_deposit_handler_mock() -> DepositPlanResponseModel:
    return DepositPlanResponseModel()

@pytest.mark.parametrize("request_input, expected_response", get_deposit_plan_valid_base_test_cases())
def test_deposit_plan_rote_with_valid_base_case(
        client: TestClient, request_input: DepositPlanRequestModel, expected_response: DepositPlanResponseModel
) -> None:
    response = client.post("/plan/deposit", json=request_input.model_dump())
    actual_response = DepositPlanResponseModel(**response.json())

    assert expected_response.result.reference_code == actual_response.result.reference_code
    assert expected_response.result.total_amount == actual_response.result.total_amount
    assert len(expected_response.result.portfolio_distribution) == len(actual_response.result.portfolio_distribution)

    for key, portfolio in enumerate(expected_response.result.portfolio_distribution):
        assert portfolio.portfolio_name == actual_response.result.portfolio_distribution[key].portfolio_name
        assert portfolio.amount == actual_response.result.portfolio_distribution[key].amount


@pytest.mark.parametrize("request_input, expected_error_message, expected_status_code", get_deposit_plan_invalid_base_test_cases())
def test_deposit_plan_route_with_invalid_base_case(
        client: TestClient,request_input: DepositPlanRequestModel, expected_error_message: str, expected_status_code: int
) -> None:
    response = client.post("/plan/deposit", json=request_input.model_dump())

    assert expected_error_message in response.text
    assert expected_status_code == response.status_code
