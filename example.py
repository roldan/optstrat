import matplotlib.pyplot as plt

from optstrat import OptionStrategy

strategy = OptionStrategy("Covered Call", 100, contract_size=100)

# 100 shares + short 1 call contract
strategy.long_underlying(100, quantity=100)
strategy.short_call(110, 2.5, quantity=1)

max_profit, max_loss = strategy.max_profit_and_loss()
net_cost = strategy.net_cost()

print(f"Max Profit: {max_profit}")
print(f"Max Loss: {max_loss}")
print(f"Cost of entering position ${net_cost}")
for leg in strategy.legs:
    print(leg)

plt.plot(strategy.underlying_prices, strategy.payoffs)
plt.title(strategy.name)
plt.fill_between(
    strategy.underlying_prices,
    strategy.payoffs,
    where=(strategy.payoffs > 0),
    facecolor='g',
    alpha=0.4,
)
plt.fill_between(
    strategy.underlying_prices,
    strategy.payoffs,
    where=(strategy.payoffs < 0),
    facecolor='r',
    alpha=0.4,
)
plt.xlabel(r'$S_T$')
plt.ylabel('P&L')
plt.show()
