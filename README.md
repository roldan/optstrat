# optstrat

A small Python library for building options strategies.

It lets you define a strategy leg by leg, calculate the payoff at expiration, and compute max profit and max loss.

## Installation

```bash
pip install optstrat
```

For plotting examples:

```bash
pip install matplotlib
```

## Usage example

Plot payoff using `matplotlib`:

```python
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
```

## Notes

- `underlying_prices` represents possible underlying prices at expiration.
- `quantity` is the number of contracts for option legs and the number of shares for underlying legs.
- `contract_size` applies only to option legs.
- `strategy.net_cost()` computes the net cost of entering the position.
- `strategy.max_profit_and_loss()` computes max profit and max loss at expiration.
