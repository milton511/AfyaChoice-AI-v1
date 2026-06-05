import math

def hormonal_probability(age_group_clinical, edu_level, marital_status, ever_been_pregnant):
    """
    Logistic regression model based on Cynthia's coefficients.
    Returns probability (0-1) that hormonal methods are suitable.
    """
    logit = -2.88859684330198  # intercept

    # Age group (one-hot)
    if age_group_clinical == "Peak Reproductive (20-34)":
        logit += 1.48142509663635
    elif age_group_clinical == "Advanced Maternal Age (35-49)":
        logit += 0.184368150894733
    # "Adolescent (15-19)" adds nothing

    # Education
    if edu_level == "Primary":
        logit += 1.04198370847373
    elif edu_level == "Secondary":
        logit += 0.778263464783876
    # "Tertiary" adds nothing

    # Marital status
    if marital_status == "Other":
        logit += -1.35350229720388
    elif marital_status == "Never married":
        logit += -1.53204479549144
    # "Married" adds nothing

    # Ever pregnant
    if ever_been_pregnant == "Yes":
        logit += 2.07691659640518

    prob = 1 / (1 + math.exp(-logit))
    return prob

# For backwards compatibility if your code calls a different function name
def predict(user_data):
    return hormonal_probability(
        user_data.get("age_group_clinical", "Peak Reproductive (20-34)"),
        user_data.get("edu_level", "Secondary"),
        user_data.get("marital_status", "Married"),
        user_data.get("ever_been_pregnant", "No")
    )