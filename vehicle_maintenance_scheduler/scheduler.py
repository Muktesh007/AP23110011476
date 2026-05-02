def knapsack(tasks, max_hours):
    n = len(tasks)
    dp = [[0]*(max_hours+1) for _ in range(n+1)]

    for i in range(1, n+1):
        d = tasks[i-1]["Duration"]
        v = tasks[i-1]["Impact"]

        for w in range(max_hours+1):
            if d <= w:
                dp[i][w] = max(v + dp[i-1][w-d], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]

    res = []
    w = max_hours

    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            res.append(tasks[i-1])
            w -= tasks[i-1]["Duration"]

    return res, dp[n][max_hours]