# -*- coding: utf-8 -*-
"""
scenario_forge: Governed Artificial Crypto AML Scenario Compiler

This library generates GOVERNED, ARTIFICIAL (NOT synthetic) crypto AML scenarios
for demos and model evaluation. This is a controlled adversarial scenario compiler.

⚠️ WARNING: All data generated is ARTIFICIAL and must be explicitly labeled as such.
For internal testing and demos only, not for production use.
"""

from .scenario import Scenario, ScenarioIntent
from .primitives import (
    Wallet, Transaction, Asset, Chain, ChainType,
    Jurisdiction, RegulatoryTier
)
from .templates import (
    cross_chain_laundering,
    mixer_ransomware_liquidation,
    sanctions_evasion_jurisdiction_hopping,
    nft_wash_trading_extraction,
    false_positive_legitimate_pattern
)
from .exporters import (
    export_json,
    export_csv_transactions,
    export_markdown_narrative
)
from .narrative import generate_narrative
from .motifs import (
    LaunderingMotif,
    PeelChain,
    CrossChainBridge,
    MixerObfuscation,
    NFTWashTrading,
    DormancyCooling,
    FalsePositiveTrap
)

__version__ = "0.1.0"
__all__ = [
    # Core classes
    'Scenario',
    'ScenarioIntent',
    'Wallet',
    'Transaction',
    'Asset',
    'Chain',
    'ChainType',
    'Jurisdiction',
    'RegulatoryTier',
    # Templates
    'cross_chain_laundering',
    'mixer_ransomware_liquidation',
    'sanctions_evasion_jurisdiction_hopping',
    'nft_wash_trading_extraction',
    'false_positive_legitimate_pattern',
    # Exporters
    'export_json',
    'export_csv_transactions',
    'export_markdown_narrative',
    # Narrative
    'generate_narrative',
    # Motifs
    'LaunderingMotif',
    'PeelChain',
    'CrossChainBridge',
    'MixerObfuscation',
    'NFTWashTrading',
    'DormancyCooling',
    'FalsePositiveTrap',
]

