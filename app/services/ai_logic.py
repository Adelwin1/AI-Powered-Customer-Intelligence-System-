def generate_resolution(category: str, title: str, description: str) -> str:
    text = (title + " " + description).lower()

    if category == "billing":
        return (
            "We detected a billing-related issue. "
            "Please allow 3–5 business days for review or refund processing."
        )

    if category == "technical":
        return (
            "This appears to be a technical issue. "
            "Try restarting the app or clearing cache. "
            "If the issue persists, our engineering team will investigate."
        )

    if category == "authentication":
        return (
            "This is an authentication issue. "
            "Please reset your password or use the 'Forgot Password' option."
        )

    return (
        "Our support team will review your request and get back to you shortly."
    )