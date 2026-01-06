# -*- coding: utf-8 -*-
"""
Scenario Templates

5 hard-coded scenario templates that combine motifs to create realistic
adversarial AML scenarios.
"""

from datetime import datetime
from decimal import Decimal

from .scenario import Scenario, ScenarioIntent
from .primitives import (
    Wallet, Asset, Chain, ChainType, Jurisdiction, RegulatoryTier
)
from .motifs import (
    PeelChain, CrossChainBridge, MixerObfuscation, NFTWashTrading,
    DormancyCooling, FalsePositiveTrap
)


# Common chains
ETHEREUM = Chain(name="Ethereum", chain_id=1, chain_type=ChainType.EVM)
POLYGON = Chain(name="Polygon", chain_id=137, chain_type=ChainType.EVM)
BITCOIN = Chain(name="Bitcoin", chain_id=0, chain_type=ChainType.UTXO)
ARBITRUM = Chain(name="Arbitrum", chain_id=42161, chain_type=ChainType.EVM)

# Common jurisdictions
US = Jurisdiction(code="US", name="United States", regulatory_tier=RegulatoryTier.STRICT)
UK = Jurisdiction(code="GB", name="United Kingdom", regulatory_tier=RegulatoryTier.MODERATE)
SG = Jurisdiction(code="SG", name="Singapore", regulatory_tier=RegulatoryTier.MODERATE)
KY = Jurisdiction(code="KY", name="Cayman Islands", regulatory_tier=RegulatoryTier.LENIENT)


def cross_chain_laundering() -> Scenario:
    """
    Template 1: Cross-chain laundering via bridge + CEX exit
    
    Intent: LAUNDERING
    Motifs: CrossChainBridge, PeelChain
    """
    scenario = Scenario(
        intent=ScenarioIntent.LAUNDERING,
        jurisdiction_assumptions=[US, SG, KY],
        motifs_used=['CrossChainBridge', 'PeelChain'],
        created_at=datetime.now()
    )
    
    # Create source wallet (sanctioned entity)
    source_addr = "0x" + "a" * 40
    source_wallet = Wallet(
        address=source_addr,
        chain=ETHEREUM,
        jurisdiction=US,
        balance=Decimal("100.0"),
        created_at=datetime.now()
    )
    
    # Create destination wallet (CEX)
    dest_addr = "0x" + "b" * 40
    dest_wallet = Wallet(
        address=dest_addr,
        chain=POLYGON,
        jurisdiction=SG,
        balance=Decimal("0"),
        created_at=datetime.now()
    )
    
    # Create asset
    asset = Asset(symbol="ETH", chain=ETHEREUM, decimals=18)
    
    # Apply CrossChainBridge motif
    bridge_motif = CrossChainBridge()
    bridge_txs, bridge_roles, bridge_weaknesses = bridge_motif.generate_subgraph(
        source_wallet=source_wallet,
        target_wallet=dest_wallet,
        asset=asset,
        params={
            'bridge_chains': [POLYGON],
            'amount': 50.0,
            'time_variance': (12, 48)
        }
    )
    
    # Apply PeelChain motif for final hops
    peel_motif = PeelChain()
    peel_txs, peel_roles, peel_weaknesses = peel_motif.generate_subgraph(
        source_wallet=dest_wallet,  # Simplified - would use intermediate wallets
        target_wallet=dest_wallet,
        asset=Asset(symbol="ETH", chain=POLYGON, decimals=18),
        params={
            'depth': 3,
            'amount': 50.0,
            'time_variance': (1, 6),
            'cost_tolerance': 0.001
        }
    )
    
    # Combine transactions (simplified - real implementation would chain motifs properly)
    all_txs = bridge_txs
    all_roles = {**bridge_roles, **peel_roles}
    all_weaknesses = bridge_weaknesses + peel_weaknesses
    
    scenario.add_transactions(all_txs, all_roles, all_weaknesses)
    
    return scenario


def mixer_ransomware_liquidation() -> Scenario:
    """
    Template 2: Mixer-based ransomware liquidation
    
    Intent: LAUNDERING (RANSOMWARE_LIQUIDATION)
    Motifs: MixerObfuscation, DormancyCooling
    """
    scenario = Scenario(
        intent=ScenarioIntent.RANSOMWARE_LIQUIDATION,
        jurisdiction_assumptions=[US, KY],
        motifs_used=['MixerObfuscation', 'DormancyCooling'],
        created_at=datetime.now()
    )
    
    # Ransomware wallet
    ransom_addr = "0x" + "c" * 40
    ransom_wallet = Wallet(
        address=ransom_addr,
        chain=ETHEREUM,
        jurisdiction=US,
        balance=Decimal("500.0"),
        created_at=datetime.now()
    )
    
    # Exit wallet
    exit_addr = "0x" + "d" * 40
    exit_wallet = Wallet(
        address=exit_addr,
        chain=ETHEREUM,
        jurisdiction=KY,
        balance=Decimal("0"),
        created_at=datetime.now()
    )
    
    asset = Asset(symbol="ETH", chain=ETHEREUM, decimals=18)
    
    # Apply MixerObfuscation
    mixer_motif = MixerObfuscation()
    mixer_txs, mixer_roles, mixer_weaknesses = mixer_motif.generate_subgraph(
        source_wallet=ransom_wallet,
        target_wallet=exit_wallet,
        asset=asset,
        params={
            'mixer_rounds': 3,
            'amount': 500.0,
            'mixer_delay': (24, 72)
        }
    )
    
    scenario.add_transactions(mixer_txs, mixer_roles, mixer_weaknesses)
    
    return scenario


def sanctions_evasion_jurisdiction_hopping() -> Scenario:
    """
    Template 3: Sanctions evasion via jurisdiction hopping
    
    Intent: SANCTIONS_EVASION
    Motifs: CrossChainBridge (with jurisdiction changes)
    """
    scenario = Scenario(
        intent=ScenarioIntent.SANCTIONS_EVASION,
        jurisdiction_assumptions=[US, SG, KY],
        motifs_used=['CrossChainBridge'],
        created_at=datetime.now()
    )
    
    # Sanctioned entity wallet (US)
    sanctioned_addr = "0x" + "e" * 40
    sanctioned_wallet = Wallet(
        address=sanctioned_addr,
        chain=ETHEREUM,
        jurisdiction=US,
        balance=Decimal("200.0"),
        created_at=datetime.now()
    )
    
    # Final destination (offshore)
    offshore_addr = "0x" + "f" * 40
    offshore_wallet = Wallet(
        address=offshore_addr,
        chain=ARBITRUM,
        jurisdiction=KY,
        balance=Decimal("0"),
        created_at=datetime.now()
    )
    
    asset = Asset(symbol="ETH", chain=ETHEREUM, decimals=18)
    
    # Apply CrossChainBridge with multiple hops
    bridge_motif = CrossChainBridge()
    bridge_txs, bridge_roles, bridge_weaknesses = bridge_motif.generate_subgraph(
        source_wallet=sanctioned_wallet,
        target_wallet=offshore_wallet,
        asset=asset,
        params={
            'bridge_chains': [POLYGON, ARBITRUM],
            'amount': 200.0,
            'time_variance': (24, 72)
        }
    )
    
    scenario.add_transactions(bridge_txs, bridge_roles, bridge_weaknesses)
    
    return scenario


def nft_wash_trading_extraction() -> Scenario:
    """
    Template 4: NFT wash trading for value extraction
    
    Intent: LAUNDERING
    Motifs: NFTWashTrading
    """
    scenario = Scenario(
        intent=ScenarioIntent.LAUNDERING,
        jurisdiction_assumptions=[US, SG],
        motifs_used=['NFTWashTrading'],
        created_at=datetime.now()
    )
    
    # Source wallet
    source_addr = "0x" + "1" * 40
    source_wallet = Wallet(
        address=source_addr,
        chain=ETHEREUM,
        jurisdiction=US,
        balance=Decimal("100.0"),
        created_at=datetime.now()
    )
    
    # Destination wallet
    dest_addr = "0x" + "2" * 40
    dest_wallet = Wallet(
        address=dest_addr,
        chain=ETHEREUM,
        jurisdiction=SG,
        balance=Decimal("0"),
        created_at=datetime.now()
    )
    
    asset = Asset(symbol="ETH", chain=ETHEREUM, decimals=18)
    
    # Apply NFTWashTrading
    nft_motif = NFTWashTrading()
    nft_txs, nft_roles, nft_weaknesses = nft_motif.generate_subgraph(
        source_wallet=source_wallet,
        target_wallet=dest_wallet,
        asset=asset,
        params={
            'wash_rounds': 5,
            'amount': 100.0,
            'time_variance': (6, 24)
        }
    )
    
    scenario.add_transactions(nft_txs, nft_roles, nft_weaknesses)
    
    return scenario


def false_positive_legitimate_pattern() -> Scenario:
    """
    Template 5: False positive trap (legitimate behavior that looks illicit)
    
    Intent: FALSE_POSITIVE_TRAP
    Motifs: FalsePositiveTrap
    """
    scenario = Scenario(
        intent=ScenarioIntent.FALSE_POSITIVE_TRAP,
        jurisdiction_assumptions=[US],
        motifs_used=['FalsePositiveTrap'],
        created_at=datetime.now()
    )
    
    # Legitimate trading wallet
    trader_addr = "0x" + "3" * 40
    trader_wallet = Wallet(
        address=trader_addr,
        chain=ETHEREUM,
        jurisdiction=US,
        balance=Decimal("50.0"),
        created_at=datetime.now()
    )
    
    # Legitimate counterparty
    counterparty_addr = "0x" + "4" * 40
    counterparty_wallet = Wallet(
        address=counterparty_addr,
        chain=ETHEREUM,
        jurisdiction=US,
        balance=Decimal("50.0"),
        created_at=datetime.now()
    )
    
    asset = Asset(symbol="ETH", chain=ETHEREUM, decimals=18)
    
    # Apply FalsePositiveTrap
    false_pos_motif = FalsePositiveTrap()
    false_pos_txs, false_pos_roles, false_pos_weaknesses = false_pos_motif.generate_subgraph(
        source_wallet=trader_wallet,
        target_wallet=counterparty_wallet,
        asset=asset,
        params={
            'pattern_type': 'high_frequency_trading',
            'amount': 50.0
        }
    )
    
    scenario.add_transactions(false_pos_txs, false_pos_roles, false_pos_weaknesses)
    
    return scenario

