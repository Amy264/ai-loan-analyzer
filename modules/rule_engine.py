def calculate_dti(monthly_debt, income):
    return monthly_debt / income


def evaluate_credit_score(score):
    if score >= 700:
        return "low_risk"
    elif score >= 650:
        return "medium_risk"
    else:
        return "high_risk"


def evaluate_dti(dti):
    if dti < 0.3:
        return "good"
    elif dti < 0.4:
        return "moderate"
    else:
        return "risky"


def evaluate_employment(years):
    if years > 3:
        return "stable"
    elif years >= 1:
        return "moderate"
    else:
        return "unstable"


def evaluate_debt_to_income_ratio(monthly_debt, monthly_income):
    """Calculate and evaluate debt-to-income ratio."""
    if monthly_income == 0:
        return {"ratio": 0, "status": "error"}
    dti = calculate_dti(monthly_debt, monthly_income)
    return {
        "ratio": round(dti, 2),
        "status": evaluate_dti(dti)
    }


def evaluate_loan(data):
    """
    Evaluate loan application based on predefined business rules.
    
    Args:
        data (dict): Application data with keys:
                     - monthly_income
                     - monthly_debt_payment
                     - credit_score
                     - employment_years
                     - loan_amount
                     - property_value
    
    Returns:
        dict: Evaluation results including risk assessment and recommendations
    """
    credit = evaluate_credit_score(data.get("credit_score", 600))

    dti_info = evaluate_debt_to_income_ratio(
        data.get("monthly_debt_payment", 0),
        data.get("monthly_income", 1)
    )

    employment = evaluate_employment(
        data.get("employment_years", 0)
    )
    
    # Calculate loan-to-value ratio if property_value available
    property_value = data.get("property_value", 0)
    loan_amount = data.get("loan_amount", 0)
    ltv_ratio = 0
    if property_value > 0:
        ltv_ratio = round((loan_amount / property_value) * 100, 2)

    return {
        "credit_risk": credit,
        "dti_ratio": dti_info["ratio"],
        "dti_status": dti_info["status"],
        "employment_status": employment,
        "loan_to_value_ratio": ltv_ratio,
        "summary": {
            "credit_risk": credit,
            "dti_status": dti_info["status"],
            "employment_status": employment,
            "ltv_status": "good" if ltv_ratio <= 80 else "risky"
        }
    }