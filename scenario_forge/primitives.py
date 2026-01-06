# -*- coding: utf-8 -*-
"""
Financial Primitives for scenario_forge

Defines core financial entities: Wallet, Transaction, Asset, Chain, Jurisdiction
All primitives enforce basic validity constraints.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, Optional


class ChainType(Enum):
    """Blockchain type enumeration"""
    EVM = "EVM"
    UTXO = "UTXO"
    OTHER = "OTHER"


class RegulatoryTier(Enum):
    """Regulatory tier enumeration"""
    STRICT = "STRICT"  # e.g., US, EU
    MODERATE = "MODERATE"  # e.g., UK, Singapore
    LENIENT = "LENIENT"  # e.g., some offshore jurisdictions
    UNREGULATED = "UNREGULATED"  # e.g., unregulated jurisdictions


@dataclass(frozen=True)
class Chain:
    """Blockchain representation"""
    name: str
    chain_id: int
    chain_type: ChainType
    
    def __str__(self) -> str:
        return f"{self.name} (chain_id: {self.chain_id})"


@dataclass(frozen=True)
class Jurisdiction:
    """Jurisdictional context"""
    code: str  # ISO 3166-1 alpha-2
    name: str
    regulatory_tier: RegulatoryTier
    
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


@dataclass(frozen=True)
class Asset:
    """Cryptocurrency asset"""
    symbol: str
    chain: Chain
    decimals: int = 18
    
    def __str__(self) -> str:
        return f"{self.symbol} on {self.chain.name}"


@dataclass
class Wallet:
    """Crypto wallet representation"""
    address: str
    chain: Chain
    jurisdiction: Jurisdiction
    balance: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate wallet"""
        if self.balance < 0:
            raise ValueError(f"Wallet balance cannot be negative: {self.balance}")
        if not self.address:
            raise ValueError("Wallet address cannot be empty")
    
    def __hash__(self) -> int:
        """Make wallet hashable for graph operations"""
        return hash((self.address, self.chain.name, self.chain.chain_id))
    
    def __eq__(self, other) -> bool:
        """Wallet equality based on address and chain"""
        if not isinstance(other, Wallet):
            return False
        return self.address == other.address and self.chain == other.chain
    
    def __str__(self) -> str:
        return f"{self.address[:10]}... ({self.chain.name})"
    
    def can_spend(self, amount: Decimal, fee: Decimal = Decimal("0")) -> bool:
        """Check if wallet has sufficient balance"""
        return self.balance >= (amount + fee)


@dataclass
class Transaction:
    """Blockchain transaction"""
    tx_id: str
    from_wallet: Wallet
    to_wallet: Wallet
    asset: Asset
    amount: Decimal
    fee: Decimal = Decimal("0")
    timestamp: datetime = field(default_factory=datetime.now)
    block_number: int = 0
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate transaction"""
        if self.amount <= 0:
            raise ValueError(f"Transaction amount must be positive: {self.amount}")
        if self.fee < 0:
            raise ValueError(f"Transaction fee cannot be negative: {self.fee}")
        if self.from_wallet.chain != self.asset.chain:
            raise ValueError(
                f"From wallet chain {self.from_wallet.chain} must match asset chain {self.asset.chain}"
            )
        if self.to_wallet.chain != self.asset.chain:
            raise ValueError(
                f"To wallet chain {self.to_wallet.chain} must match asset chain {self.asset.chain}"
            )
        # Note: Balance validation is relaxed for artificial scenario generation
        # In real blockchain systems, this would be strictly enforced
        # For scenario generation, wallets represent entities, not actual blockchain state
    
    def __hash__(self) -> int:
        """Make transaction hashable"""
        return hash(self.tx_id)
    
    def __eq__(self, other) -> bool:
        """Transaction equality based on tx_id"""
        if not isinstance(other, Transaction):
            return False
        return self.tx_id == other.tx_id
    
    def __str__(self) -> str:
        return f"{self.tx_id[:12]}... {self.amount} {self.asset.symbol} ({self.from_wallet} -> {self.to_wallet})"
    
    def to_dict(self) -> Dict:
        """Convert transaction to dictionary for serialization"""
        return {
            "tx_id": self.tx_id,
            "from_address": self.from_wallet.address,
            "to_address": self.to_wallet.address,
            "asset_symbol": self.asset.symbol,
            "amount": str(self.amount),
            "fee": str(self.fee),
            "timestamp": self.timestamp.isoformat(),
            "block_number": self.block_number,
            "metadata": self.metadata
        }

