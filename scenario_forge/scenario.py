# -*- coding: utf-8 -*-
"""
Scenario Class

Core Scenario class that orchestrates motifs, maintains transaction graphs,
and provides provenance metadata with cryptographic integrity.
"""

import json
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4
import networkx as nx

from .primitives import Wallet, Transaction, Jurisdiction
from .crypto import compute_scenario_hash


class ScenarioIntent(Enum):
    """Scenario intent enumeration"""
    SANCTIONS_EVASION = "SANCTIONS_EVASION"
    LAUNDERING = "LAUNDERING"
    FALSE_POSITIVE_TRAP = "FALSE_POSITIVE_TRAP"
    RANSOMWARE_LIQUIDATION = "RANSOMWARE_LIQUIDATION"
    TAX_EVASION = "TAX_EVASION"


class Scenario:
    """AML scenario with transaction graph, provenance, and integrity hash"""
    
    def __init__(
        self,
        scenario_id: Optional[str] = None,
        intent: ScenarioIntent = ScenarioIntent.LAUNDERING,
        jurisdiction_assumptions: Optional[List[Jurisdiction]] = None,
        motifs_used: Optional[List[str]] = None,
        created_at: Optional[datetime] = None
    ):
        self.scenario_id = scenario_id or str(uuid4())
        self.intent = intent
        self.jurisdiction_assumptions = jurisdiction_assumptions or []
        self.motifs_used = motifs_used or []
        self.created_at = created_at or datetime.now()
        
        # Transaction graph (NetworkX DiGraph)
        self.transaction_graph = nx.DiGraph()
        
        # Entity roles mapping
        self.entity_roles: Dict[str, str] = {}
        
        # AML weaknesses identified
        self.aml_weaknesses: List[str] = []
        
        # Provenance metadata
        self.provenance: Dict = {
            'generator': 'scenario_forge',
            'version': '0.1.0',
            'artificial_data_warning': 'ARTIFICIAL_DATA_DO_NOT_USE_FOR_REAL_CASES'
        }
        
        # Integrity hash (computed after transactions are added)
        self.scenario_hash: Optional[str] = None
    
    def add_transactions(self, transactions: List[Transaction], entity_roles: Dict[str, str], aml_weaknesses: List[str]):
        """
        Add transactions to the scenario graph.
        
        Args:
            transactions: List of Transaction objects
            entity_roles: Dict mapping wallet addresses to roles
            aml_weaknesses: List of AML weakness strings
        """
        # Add wallets as nodes
        wallets_seen = set()
        for tx in transactions:
            if tx.from_wallet.address not in wallets_seen:
                self.transaction_graph.add_node(
                    tx.from_wallet.address,
                    wallet=tx.from_wallet,
                    role=entity_roles.get(tx.from_wallet.address, 'unknown')
                )
                wallets_seen.add(tx.from_wallet.address)
            
            if tx.to_wallet.address not in wallets_seen:
                self.transaction_graph.add_node(
                    tx.to_wallet.address,
                    wallet=tx.to_wallet,
                    role=entity_roles.get(tx.to_wallet.address, 'unknown')
                )
                wallets_seen.add(tx.to_wallet.address)
            
            # Add transaction as edge
            self.transaction_graph.add_edge(
                tx.from_wallet.address,
                tx.to_wallet.address,
                transaction=tx,
                tx_id=tx.tx_id,
                amount=str(tx.amount),
                asset=tx.asset.symbol,
                timestamp=tx.timestamp.isoformat()
            )
        
        # Update entity roles
        self.entity_roles.update(entity_roles)
        
        # Update AML weaknesses
        for weakness in aml_weaknesses:
            if weakness not in self.aml_weaknesses:
                self.aml_weaknesses.append(weakness)
        
        # Recompute hash after adding transactions
        self.scenario_hash = self.compute_integrity_hash()
    
    def compute_integrity_hash(self) -> str:
        """
        Compute SHA-256 integrity hash of scenario.
        
        Returns:
            Hexadecimal hash string
        """
        # Create canonical representation
        scenario_data = {
            'scenario_id': self.scenario_id,
            'intent': self.intent.value,
            'created_at': self.created_at.isoformat(),
            'jurisdiction_assumptions': [
                {'code': j.code, 'name': j.name, 'tier': j.regulatory_tier.value}
                for j in self.jurisdiction_assumptions
            ],
            'motifs_used': self.motifs_used,
            'entity_roles': self.entity_roles,
            'aml_weaknesses': sorted(self.aml_weaknesses),
            'transaction_count': len(list(self.transaction_graph.edges()))
        }
        
        # Add transaction data (sorted by tx_id for determinism)
        transactions_list = []
        for from_addr, to_addr, data in self.transaction_graph.edges(data=True):
            tx = data['transaction']
            transactions_list.append({
                'tx_id': tx.tx_id,
                'from': from_addr,
                'to': to_addr,
                'amount': str(tx.amount),
                'asset': tx.asset.symbol,
                'timestamp': tx.timestamp.isoformat()
            })
        
        transactions_list.sort(key=lambda x: x['tx_id'])
        scenario_data['transactions'] = transactions_list
        
        return compute_scenario_hash(scenario_data)
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate scenario graph consistency.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check graph is not empty
        if self.transaction_graph.number_of_nodes() == 0:
            errors.append("Scenario graph is empty")
        
        # Check all transactions have valid timestamps
        for from_addr, to_addr, data in self.transaction_graph.edges(data=True):
            tx = data['transaction']
            if tx.timestamp > datetime.now():
                errors.append(f"Transaction {tx.tx_id} has future timestamp")
        
        # Check entity roles are present
        if not self.entity_roles:
            errors.append("No entity roles defined")
        
        # Check AML weaknesses are present
        if not self.aml_weaknesses:
            errors.append("No AML weaknesses identified")
        
        return len(errors) == 0, errors
    
    def get_risk_summary(self) -> Dict:
        """
        Generate risk summary statistics.
        
        Returns:
            Dictionary with risk metrics
        """
        transactions = [data['transaction'] for _, _, data in self.transaction_graph.edges(data=True)]
        
        if not transactions:
            return {
                'total_transactions': 0,
                'entities_involved': 0,
                'time_span_days': 0,
                'total_amount': '0',
                'unique_assets': [],
                'unique_chains': []
            }
        
        timestamps = [tx.timestamp for tx in transactions]
        time_span = (max(timestamps) - min(timestamps)).total_seconds() / 86400  # days
        
        total_amount = sum(tx.amount for tx in transactions)
        unique_assets = list(set(tx.asset.symbol for tx in transactions))
        unique_chains = list(set(tx.asset.chain.name for tx in transactions))
        
        return {
            'total_transactions': len(transactions),
            'entities_involved': self.transaction_graph.number_of_nodes(),
            'time_span_days': round(time_span, 2),
            'total_amount': str(total_amount),
            'unique_assets': unique_assets,
            'unique_chains': unique_chains,
            'aml_weaknesses_count': len(self.aml_weaknesses),
            'motifs_used': self.motifs_used
        }
    
    def to_dict(self) -> Dict:
        """
        Convert scenario to dictionary for serialization.
        
        Returns:
            Dictionary representation
        """
        transactions = []
        for from_addr, to_addr, data in self.transaction_graph.edges(data=True):
            tx = data['transaction']
            transactions.append(tx.to_dict())
        
        return {
            'scenario_id': self.scenario_id,
            'intent': self.intent.value,
            'created_at': self.created_at.isoformat(),
            'jurisdiction_assumptions': [
                {
                    'code': j.code,
                    'name': j.name,
                    'regulatory_tier': j.regulatory_tier.value
                }
                for j in self.jurisdiction_assumptions
            ],
            'motifs_used': self.motifs_used,
            'entity_roles': self.entity_roles,
            'aml_weaknesses': self.aml_weaknesses,
            'transactions': transactions,
            'scenario_hash': self.scenario_hash,
            'provenance': self.provenance,
            'artificial_data_warning': 'ARTIFICIAL_DATA_DO_NOT_USE_FOR_REAL_CASES'
        }

