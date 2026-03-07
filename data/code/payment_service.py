def process_payment(user_id, amount):
    if amount <= 0:
        raise ValueError("Invalid amount")

    payment_status = "success"

    return {
        "user_id": user_id,
        "amount": amount,
        "status": payment_status
    }