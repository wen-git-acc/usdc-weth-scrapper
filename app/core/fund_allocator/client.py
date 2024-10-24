from decimal import Decimal
from typing import Literal
from app.core.fund_allocator.model import DepositPlanDetail
from app.core.helper.client import HelperClient
from app.routes.deposit_route.models import DepositDetail, DepositPlan, DistributedFundResult, PortfolioDetails
from app.core.config import app_config


class FundAllocatorClient:
    """
    A Client consist of function helps to allocate fund to different portfolio 
    """

    def __init__(self, helper_client: HelperClient) -> None:
        self.__helper_client = helper_client

    """
    Main function to distribute fund to different portfolio.
    """
    def distribute_funds(self, deposit_plans: list[DepositPlan], deposit_details: list[DepositDetail]) -> DistributedFundResult:

        if len(deposit_plans) > 2:
            raise ValueError("Deposit plan is more than 2.")

        plan_detail_map: dict[Literal["one-time", "montly"], DepositPlanDetail] = {}
        portfolio_distribution_map: dict[str, Decimal] = {}
        unique_deposits_plan: set[str] = set()
        for deposit_plan in deposit_plans:

            # Handle edge case like duplicate deposit plan found.
            if deposit_plan.plan_name in unique_deposits_plan:
                raise ValueError(f"Duplicate deposit plan found {deposit_plan.plan_name}")
            else:
                unique_deposits_plan.add(deposit_plan.plan_name)

            # Handle edge case like deposit plan portfolio allocation is empty.
            if deposit_plan.portfolio_details is None or len(deposit_plan.portfolio_details) == 0:
                continue
            
            plan_detail_map[deposit_plan.plan_name] = self.__helper_client.get_portfolio_detail_from_plan(
                portfolio_details=deposit_plan.portfolio_details, 
                portfolio_distribution_map=portfolio_distribution_map
                )

        # Handle edge case like no deposit plan is found form reqeust.
        if not self.is_valid_plan(plan_detail_map):
            raise ValueError(f"Invalid deposit plan details provided {plan_detail_map}")
            

        one_time_plan = plan_detail_map.get(app_config.one_time_plan_name)
        monthly_plan = plan_detail_map.get(app_config.monthly_plan_name)

        is_both_plan = bool(one_time_plan) and bool(monthly_plan)
        is_one_time_plan = bool(one_time_plan) and not bool(monthly_plan)
        is_monthly_plan = bool(monthly_plan) and not bool(one_time_plan)   

        reference_codes: set[str] = set()

        total_deposit_amount: Decimal = Decimal(str(0.00))

        for deposit in deposit_details:



            reference_codes.add(deposit.reference_code)

            deposit_amount = Decimal(str(deposit.amount))

            # handle edge case like deposit amount is 0
            if deposit_amount == Decimal('0.00'):
                continue

            if deposit_amount < Decimal('0.00'):
                raise ValueError(f"Deposit amount is negative {deposit_amount}")

            total_deposit_amount += deposit_amount

            if is_both_plan:
                assert one_time_plan is not None, "one_time_plan cannot be None"
                assert monthly_plan is not None, "monthly_plan cannot be None"

                remaining_amount = self.one_time_plan_distribution(
                    plan_detail=one_time_plan, 
                    deposit_amount=deposit_amount, 
                    has_other_plan=True, 
                    portfolio_distribution_map=portfolio_distribution_map
                    )
                if remaining_amount > Decimal('0.00'):
                    self.monthly_plan_distribution(
                        plan_detail=monthly_plan, 
                        deposit_amount=remaining_amount, 
                        portfolio_distribution_map=portfolio_distribution_map
                        )

        
        if is_one_time_plan:
            assert one_time_plan is not None, "one_time_plan cannot be None"
            self.one_time_plan_distribution(
                plan_detail=one_time_plan,
                deposit_amount=total_deposit_amount, 
                has_other_plan=False, 
                portfolio_distribution_map=portfolio_distribution_map
                )

        if is_monthly_plan:
            assert monthly_plan is not None, "monthly_plan cannot be None"
            self.monthly_plan_distribution(
                plan_detail=monthly_plan, 
                deposit_amount=total_deposit_amount, 
                portfolio_distribution_map=portfolio_distribution_map
                )


        return self.get_distributed_fund_result(
            portfolio_distribution_map=portfolio_distribution_map, 
            reference_code=reference_codes, 
            total_deposit_amount=total_deposit_amount
            )
        

    """
    To validate if correct plan is received.
    """
    def is_valid_plan (self, plan_detail_dict: dict[Literal["one-time", "montly"], DepositPlanDetail]) -> bool:
        if plan_detail_dict.get(app_config.one_time_plan_name) is None and plan_detail_dict.get(app_config.monthly_plan_name) is None:
            return False
        return True

    """Used to distribute fund by ratio"""
    def distribute_funds_by_ratio(self, plan_detail: DepositPlanDetail, deposit_amount: Decimal, portfolio_distribution_map: dict[str, Decimal]):

        cumulative_amount_check: Decimal = Decimal("0.00")
        total_amount = plan_detail.total_amount

        if total_amount == 0:
            return

        for index, amount in enumerate(plan_detail.individual_amount):
            portfolio_name = plan_detail.portfolio_names[index]
            distributed_amount = (amount/total_amount) * deposit_amount
            cumulative_amount_check += distributed_amount
            portfolio_distribution_map[portfolio_name] += distributed_amount  

        if round(cumulative_amount_check,2) != round(deposit_amount,2):
            raise ValueError("Total amount and individual amount does not match")


    """One time Plan Distribution, will return remaining amount"""
    def one_time_plan_distribution(self, plan_detail: DepositPlanDetail, deposit_amount: Decimal, has_other_plan: bool, portfolio_distribution_map: dict[str, Decimal]) -> Decimal:

        if not has_other_plan:
            self.distribute_funds_by_ratio(
                plan_detail=plan_detail, 
                deposit_amount=deposit_amount, 
                portfolio_distribution_map=portfolio_distribution_map
                )
            return Decimal("0.00")
            
        ## In case of deposit is less than total amount.
        if deposit_amount >= plan_detail.total_amount:
            deposit_amount -= plan_detail.total_amount
            cumulative_amount_check: Decimal = Decimal("0.00")
            for index, amount in enumerate(plan_detail.individual_amount):
                portfolio_name = plan_detail.portfolio_names[index]
                portfolio_distribution_map[portfolio_name] += amount
                cumulative_amount_check += amount

            if round(cumulative_amount_check,2) != round(plan_detail.total_amount,2):
                raise ValueError("Total amount and individual amount does not match")

        return deposit_amount
    

    """Monthly Plan Distribution by ratio"""
    def monthly_plan_distribution(self, plan_detail: DepositPlanDetail, deposit_amount: Decimal, portfolio_distribution_map: dict[str, Decimal]):
        self.distribute_funds_by_ratio(plan_detail=plan_detail, deposit_amount=deposit_amount, portfolio_distribution_map=portfolio_distribution_map)


    """Get the final result distribution"""
    def get_distributed_fund_result(self, portfolio_distribution_map: dict[str, Decimal], reference_code: set[str], total_deposit_amount: Decimal) -> DistributedFundResult:
        result = DistributedFundResult()

        if len(reference_code) != 1:
            raise ValueError("Reference code is not unique")
        
        cumulative_total_amount: Decimal = Decimal("0.00")
        for portfolio_name, amount in portfolio_distribution_map.items():
            portfolio_amount = amount
            result.portfolio_distribution.append(PortfolioDetails(portfolio_name=portfolio_name, amount=float(round(portfolio_amount,2))))
            cumulative_total_amount += portfolio_amount

        result.total_amount = float(round(cumulative_total_amount,2))
        result.reference_code = reference_code.pop()

        if round(cumulative_total_amount,2) != round(total_deposit_amount,2):
            raise ValueError("Total amount and individual amount does not match")
        
        return result