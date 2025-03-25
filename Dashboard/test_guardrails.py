# Import Guard and Validator
from guardrails.hub import DetectPII
from guardrails import Guard


# Setup Guard
guard = Guard().use(
    DetectPII, ["EMAIL_ADDRESS", "PHONE_NUMBER"], "exception"
)

guard.validate("Good morning!")  # Validator passes
try:
    guard.validate(
        "If interested, apply at not_a_real_email@guardrailsai.com"
    )  # Validator fails
except Exception as e:
    print(e)