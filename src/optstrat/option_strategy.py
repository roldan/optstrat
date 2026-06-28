from enum import Enum

import numpy as np

class Kind(Enum):
    CALL = 'call'
    PUT = 'put'
    UNDERLYING = 'underlying'

class Side(Enum):
    LONG = 1
    SHORT = -1

class Leg:

    def __init__(self, kind: Kind, side: Side, entry_price, quantity=1, K=None):
        self.kind = kind
        self.side = side
        self.entry_price = entry_price
        self.quantity = quantity
        self.K = K
    
    def __repr__(self):
        side = self.side.name
        qty = f' x{self.quantity}' if self.quantity != 1 else ''
        if self.kind == Kind.UNDERLYING:
            return f'{side} {self.kind.value} @ {self.entry_price}{qty}'
        return f'{side} {self.kind.value} {self.K} @ {self.entry_price}{qty}'

class OptionStrategy:
    """Build an option strategy and compute payoff at a single expiration.

    All legs are assumed to share the same expiration.

    Quantity semantics:
    - option legs use `quantity` as number of contracts
    - underlying legs use `quantity` as number of shares

    `contract_size` applies only to option legs.
    """

    def __init__(self, name, S0, spot_range=0.5, step=1, contract_size=100):
        self.name = name
        self.S0 = S0
        self.contract_size = contract_size
        self.underlying_prices = np.arange(S0 * spot_range, S0 * (1 + spot_range), step)
        self.payoffs = np.zeros_like(self.underlying_prices, dtype=float)
        self.legs = []
           
    def _apply(self, kind: Kind, side: Side, entry_price, quantity=1, K=None):
        if kind == Kind.CALL:
            intrinsic = np.maximum(self.underlying_prices - K, 0)
            payoffs = (side.value * intrinsic - side.value * entry_price) * quantity * self.contract_size
        elif kind == Kind.PUT:
            intrinsic = np.maximum(K - self.underlying_prices, 0)
            payoffs = (side.value * intrinsic - side.value * entry_price) * quantity * self.contract_size
        elif kind == Kind.UNDERLYING:
            payoffs = side.value * (self.underlying_prices - entry_price) * quantity

        self.payoffs += payoffs
        self.legs.append(Leg(kind, side, entry_price, quantity, K=K))

    def long_call(self, K, entry_price, quantity=1):
        """Add a long call.

        Parameters:
            K: Strike price.
            entry_price: Premium paid per contract.
            quantity: Number of option contracts.
        """
        self._apply(Kind.CALL, Side.LONG, entry_price, quantity, K=K)
    
    def short_call(self, K, entry_price, quantity=1):
        """Add a short call.

        Parameters:
            K: Strike price.
            entry_price: Premium received per contract.
            quantity: Number of option contracts.
        """
        self._apply(Kind.CALL, Side.SHORT, entry_price, quantity, K=K)
    
    def long_put(self, K, entry_price, quantity=1):
        """Add a long put.

        Parameters:
            K: Strike price.
            entry_price: Premium paid per contract.
            quantity: Number of option contracts.
        """
        self._apply(Kind.PUT, Side.LONG, entry_price, quantity, K=K)
      
    def short_put(self, K, entry_price, quantity=1):
        """Add a short put.

        Parameters:
            K: Strike price.
            entry_price: Premium received per contract.
            quantity: Number of option contracts.
        """
        self._apply(Kind.PUT, Side.SHORT, entry_price, quantity, K=K)

    def long_underlying(self, entry_price, quantity=1):
        """Add a long underlying position.

        Parameters:
            entry_price: Entry price per share.
            quantity: Number of shares.
        """
        self._apply(Kind.UNDERLYING, Side.LONG, entry_price, quantity)

    def short_underlying(self, entry_price, quantity=1):
        """Add a short underlying position.

        Parameters:
            entry_price: Entry price per share.
            quantity: Number of shares.
        """
        self._apply(Kind.UNDERLYING, Side.SHORT, entry_price, quantity)

    def net_cost(self):
        """Return the net cost of entering the strategy."""
        return sum(
            leg.entry_price * leg.quantity * leg.side.value * self.contract_size
            if leg.kind in (Kind.CALL, Kind.PUT)
            else leg.entry_price * leg.quantity * leg.side.value
            for leg in self.legs
        )

    def max_profit_and_loss(self):
        """Return max profit and max loss at expiration."""
        prices = {0}
        for leg in self.legs:
            if leg.K is not None:
                prices.add(leg.K)

        def payoff_at(price):
            payoff = 0
            for leg in self.legs:
                if leg.kind == Kind.CALL:
                    intrinsic = max(price - leg.K, 0)
                    payoff += (leg.side.value * intrinsic - leg.side.value * leg.entry_price) * leg.quantity * self.contract_size
                elif leg.kind == Kind.PUT:
                    intrinsic = max(leg.K - price, 0)
                    payoff += (leg.side.value * intrinsic - leg.side.value * leg.entry_price) * leg.quantity * self.contract_size
                elif leg.kind == Kind.UNDERLYING:
                    payoff += leg.side.value * (price - leg.entry_price) * leg.quantity
            return payoff

        slope = 0
        for leg in self.legs:
            if leg.kind == Kind.CALL:
                slope += leg.side.value * leg.quantity * self.contract_size
            elif leg.kind == Kind.UNDERLYING:
                slope += leg.side.value * leg.quantity

        payoffs = [payoff_at(price) for price in sorted(prices)]
        max_profit = max(payoffs)
        max_loss = min(payoffs)

        if slope > 0:
            max_profit = np.inf
        elif slope < 0:
            max_loss = -np.inf

        return max_profit, max_loss
