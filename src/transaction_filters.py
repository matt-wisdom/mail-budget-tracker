FILTERS = [
    # Transaction / Payment combinations (original filters)
    ["transaction", "success"],
    ["transaction", "fail"],
    ["transaction", "unsuccessful"],
    ["transaction", "new"],
    ["transaction", "notification"],
    ["transaction", "alert"],
    ["payment", "success"],
    ["payment", "fail"],
    ["payment", "unsuccessful"],
    ["payment", "new"],
    ["payment", "notification"],
    ["payment", "alert"],
    ["new", "payment"],
    ["bank", "transaction"],
    ["bank", "payment"],
    ["account", "transaction"],
    ["account", "payment"],
    ["transaction", "declined"],
    ["payment", "declined"],
    ["transaction", "completed"],
    ["payment", "completed"],
    ["transaction", "received"],
    ["payment", "received"],
    # Withdrawal combinations
    ["withdrawal", "success"],
    ["withdrawal", "fail"],
    ["withdrawal", "unsuccessful"],
    ["withdrawal", "notification"],
    ["withdrawal", "alert"],
    ["withdrawal", "completed"],
    ["withdrawal", "received"],
    # Deposit combinations
    ["deposit", "success"],
    ["deposit", "fail"],
    ["deposit", "unsuccessful"],
    ["deposit", "notification"],
    ["deposit", "alert"],
    ["deposit", "completed"],
    ["deposit", "received"],
    # Funding combinations
    ["funding", "success"],
    ["funding", "fail"],
    ["funding", "unsuccessful"],
    ["funding", "notification"],
    ["funding", "alert"],
    ["funding", "completed"],
    ["funding", "received"],
    # Additional mixed combinations
    ["withdrawal", "deposit"],  # if alerts mention both terms
    ["funding", "deposit"],
    ["funding", "withdrawal"],
]
