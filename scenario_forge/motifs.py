# -*- coding: utf-8 -*-
"""
Laundering Motifs

Reusable strategy classes that generate transaction subgraphs representing
specific money laundering techniques. Each motif accepts parameters and
outputs transactions with annotated AML weaknesses.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple
import random

from .primitives import (
    Wallet, Transaction, Asset, Chain, ChainType, Jurisdiction, RegulatoryTier
)


class LaunderingMotif(ABC):
    """Abstract base class for laundering strategy motifs"""
    
    @abstractmethod
    def generate_subgraph(
        self,
        source_wallet: Wallet,
        target_wallet: Wallet,
        asset: Asset,
        params: Dict
    ) -> Tuple[List[Transaction], Dict[str, str], List[str]]:
        """
        Generate a transaction subgraph representing this laundering technique.
        
        Args:
            source_wallet: Initial source wallet
            target_wallet: Final destination wallet
            asset: Asset being transferred
            params: Motif-specific parameters
        
        Returns:
            Tuple of:
            - List of Transaction objects
            - Dict mapping wallet addresses to entity roles
            - List of AML weakness strings this motif targets
        """
        pass


class PeelChain(LaunderingMotif):
    """
    Peel chain motif: Creates a chain of small transfers to break up large amounts.
    
    Parameters:
        depth: Number of hops in the chain (default: 5)
        time_variance: Hours between transactions (default: 1-6)
        cost_tolerance: Maximum fee per transaction (default: 0.001)
    """
    
    def generate_subgraph(
        self,
        source_wallet: Wallet,
        target_wallet: Wallet,
        asset: Asset,
        params: Dict
    ) -> Tuple[List[Transaction], Dict[str, str], List[str]]:
        depth = params.get('depth', 5)
        time_variance = params.get('time_variance', (1, 6))  # hours
        cost_tolerance = Decimal(str(params.get('cost_tolerance', 0.001)))
        total_amount = Decimal(str(params.get('amount', 10.0)))
        
        transactions = []
        entity_roles = {source_wallet.address: 'source', target_wallet.address: 'destination'}
        
        # Create intermediate wallets
        intermediate_wallets = []
        current_wallet = source_wallet
        current_time = datetime.now()
        amount_per_hop = total_amount / Decimal(depth)
        
        for i in range(depth - 1):
            # Create intermediate wallet
            intermediate_addr = f"0x{''.join(random.choices('0123456789abcdef', k=40))}"
            intermediate_wallet = Wallet(
                address=intermediate_addr,
                chain=asset.chain,
                jurisdiction=current_wallet.jurisdiction,
                balance=Decimal("0"),
                created_at=current_time
            )
            intermediate_wallets.append(intermediate_wallet)
            entity_roles[intermediate_addr] = 'intermediate_peel'
            
            # Create transaction
            tx_id = f"peel_{i}_{random.randint(10000, 99999)}"
            fee = cost_tolerance * Decimal(random.uniform(0.5, 1.0))
            
            tx = Transaction(
                tx_id=tx_id,
                from_wallet=current_wallet,
                to_wallet=intermediate_wallet,
                asset=asset,
                amount=amount_per_hop,
                fee=fee,
                timestamp=current_time,
                block_number=0,
                metadata={'motif': 'peel_chain', 'hop': i}
            )
            
            transactions.append(tx)
            
            # Update balances (simplified - in real scenario, balances would be tracked)
            current_wallet = intermediate_wallet
            current_time += timedelta(hours=random.uniform(*time_variance))
        
        # Final hop to target
        final_tx_id = f"peel_final_{random.randint(10000, 99999)}"
        final_fee = cost_tolerance * Decimal(random.uniform(0.5, 1.0))
        
        final_tx = Transaction(
            tx_id=final_tx_id,
            from_wallet=current_wallet,
            to_wallet=target_wallet,
            asset=asset,
            amount=amount_per_hop,
            fee=final_fee,
            timestamp=current_time,
            block_number=0,
            metadata={'motif': 'peel_chain', 'hop': depth - 1}
        )
        transactions.append(final_tx)
        
        aml_weaknesses = [
            "Transaction clustering gaps",
            "Small amount thresholds bypass",
            "Temporal pattern obfuscation"
        ]
        
        return transactions, entity_roles, aml_weaknesses


class CrossChainBridge(LaunderingMotif):
    """
    Cross-chain bridge motif: Transfers assets across blockchains via bridges.
    
    Parameters:
        bridge_chains: List of Chain objects to bridge through (default: auto-generated)
        time_variance: Hours between bridge hops (default: 12-48)
    """
    
    def generate_subgraph(
        self,
        source_wallet: Wallet,
        target_wallet: Wallet,
        asset: Asset,
        params: Dict
    ) -> Tuple[List[Transaction], Dict[str, str], List[str]]:
        bridge_chains = params.get('bridge_chains', [])
        time_variance = params.get('time_variance', (12, 48))
        amount = Decimal(str(params.get('amount', 10.0)))
        
        transactions = []
        entity_roles = {source_wallet.address: 'source', target_wallet.address: 'destination'}
        
        # Create bridge wallets if chains provided
        if bridge_chains:
            current_wallet = source_wallet
            current_time = datetime.now()
            
            for i, bridge_chain in enumerate(bridge_chains):
                # Create bridge wallet on new chain
                bridge_addr = f"0x{''.join(random.choices('0123456789abcdef', k=40))}"
                bridge_wallet = Wallet(
                    address=bridge_addr,
                    chain=bridge_chain,
                    jurisdiction=current_wallet.jurisdiction,
                    balance=Decimal("0"),
                    created_at=current_time
                )
                entity_roles[bridge_addr] = f'bridge_{i}'
                
                # Bridge transaction (simplified - assumes wrapped asset)
                bridge_tx_id = f"bridge_{i}_{random.randint(10000, 99999)}"
                bridge_fee = Decimal("0.01")
                
                bridge_tx = Transaction(
                    tx_id=bridge_tx_id,
                    from_wallet=current_wallet,
                    to_wallet=bridge_wallet,
                    asset=asset,  # Simplified - real bridges would use wrapped assets
                    amount=amount,
                    fee=bridge_fee,
                    timestamp=current_time,
                    block_number=0,
                    metadata={'motif': 'cross_chain_bridge', 'chain': bridge_chain.name}
                )
                
                transactions.append(bridge_tx)
                current_wallet = bridge_wallet
                current_time += timedelta(hours=random.uniform(*time_variance))
            
            # Final bridge to target
            final_bridge_tx_id = f"bridge_final_{random.randint(10000, 99999)}"
            final_bridge_tx = Transaction(
                tx_id=final_bridge_tx_id,
                from_wallet=current_wallet,
                to_wallet=target_wallet,
                asset=asset,
                amount=amount,
                fee=Decimal("0.01"),
                timestamp=current_time,
                block_number=0,
                metadata={'motif': 'cross_chain_bridge', 'final': True}
            )
            transactions.append(final_bridge_tx)
        else:
            # Single bridge hop (simplified)
            bridge_tx_id = f"bridge_{random.randint(10000, 99999)}"
            bridge_tx = Transaction(
                tx_id=bridge_tx_id,
                from_wallet=source_wallet,
                to_wallet=target_wallet,
                asset=asset,
                amount=amount,
                fee=Decimal("0.01"),
                timestamp=datetime.now(),
                block_number=0,
                metadata={'motif': 'cross_chain_bridge'}
            )
            transactions.append(bridge_tx)
        
        aml_weaknesses = [
            "Cross-chain analysis gaps",
            "Bridge correlation weaknesses",
            "Multi-chain jurisdiction arbitrage"
        ]
        
        return transactions, entity_roles, aml_weaknesses


class MixerObfuscation(LaunderingMotif):
    """
    Mixer obfuscation motif: Uses mixing services to break transaction links.
    
    Parameters:
        mixer_rounds: Number of mixer iterations (default: 3)
        mixer_delay: Hours between mixer entry/exit (default: 24-72)
    """
    
    def generate_subgraph(
        self,
        source_wallet: Wallet,
        target_wallet: Wallet,
        asset: Asset,
        params: Dict
    ) -> Tuple[List[Transaction], Dict[str, str], List[str]]:
        mixer_rounds = params.get('mixer_rounds', 3)
        mixer_delay = params.get('mixer_delay', (24, 72))
        amount = Decimal(str(params.get('amount', 10.0)))
        
        transactions = []
        entity_roles = {
            source_wallet.address: 'source',
            target_wallet.address: 'destination'
        }
        
        current_wallet = source_wallet
        current_time = datetime.now()
        
        for i in range(mixer_rounds):
            # Mixer entry wallet (service wallet)
            mixer_entry_addr = f"mixer_entry_{i}_{random.randint(10000, 99999)}"
            mixer_entry = Wallet(
                address=mixer_entry_addr,
                chain=asset.chain,
                jurisdiction=current_wallet.jurisdiction,
                balance=Decimal("0"),
                created_at=current_time
            )
            entity_roles[mixer_entry_addr] = f'mixer_entry_{i}'
            
            # Entry transaction
            entry_tx_id = f"mixer_entry_{i}_{random.randint(10000, 99999)}"
            entry_tx = Transaction(
                tx_id=entry_tx_id,
                from_wallet=current_wallet,
                to_wallet=mixer_entry,
                asset=asset,
                amount=amount,
                fee=Decimal("0.005"),
                timestamp=current_time,
                block_number=0,
                metadata={'motif': 'mixer_obfuscation', 'type': 'entry', 'round': i}
            )
            transactions.append(entry_tx)
            
            # Mixer exit (after delay)
            mixer_exit_addr = f"mixer_exit_{i}_{random.randint(10000, 99999)}"
            mixer_exit = Wallet(
                address=mixer_exit_addr,
                chain=asset.chain,
                jurisdiction=current_wallet.jurisdiction,
                balance=Decimal("0"),
                created_at=current_time + timedelta(hours=random.uniform(*mixer_delay))
            )
            entity_roles[mixer_exit_addr] = f'mixer_exit_{i}'
            
            current_time += timedelta(hours=random.uniform(*mixer_delay))
            
            # Exit transaction (slightly less due to mixer fees)
            exit_tx_id = f"mixer_exit_{i}_{random.randint(10000, 99999)}"
            mixer_fee = amount * Decimal("0.03")  # 3% mixer fee
            exit_tx = Transaction(
                tx_id=exit_tx_id,
                from_wallet=mixer_entry,  # Simplified - real mixers are more complex
                to_wallet=mixer_exit,
                asset=asset,
                amount=amount - mixer_fee,
                fee=Decimal("0.005"),
                timestamp=current_time,
                block_number=0,
                metadata={'motif': 'mixer_obfuscation', 'type': 'exit', 'round': i}
            )
            transactions.append(exit_tx)
            
            current_wallet = mixer_exit
        
        # Final transfer to target
        final_tx_id = f"mixer_final_{random.randint(10000, 99999)}"
        final_tx = Transaction(
            tx_id=final_tx_id,
            from_wallet=current_wallet,
            to_wallet=target_wallet,
            asset=asset,
            amount=amount - (amount * Decimal("0.03") * mixer_rounds),
            fee=Decimal("0.001"),
            timestamp=current_time + timedelta(hours=random.uniform(1, 6)),
            block_number=0,
            metadata={'motif': 'mixer_obfuscation', 'final': True}
        )
        transactions.append(final_tx)
        
        aml_weaknesses = [
            "Mixer exit correlation gaps",
            "Temporal pattern obfuscation",
            "Transaction graph fragmentation"
        ]
        
        return transactions, entity_roles, aml_weaknesses


class NFTWashTrading(LaunderingMotif):
    """
    NFT wash trading motif: Circular NFT trades to extract value.
    
    Parameters:
        wash_rounds: Number of circular trades (default: 5)
        time_variance: Hours between trades (default: 6-24)
    """
    
    def generate_subgraph(
        self,
        source_wallet: Wallet,
        target_wallet: Wallet,
        asset: Asset,
        params: Dict
    ) -> Tuple[List[Transaction], Dict[str, str], List[str]]:
        wash_rounds = params.get('wash_rounds', 5)
        time_variance = params.get('time_variance', (6, 24))
        base_amount = Decimal(str(params.get('amount', 5.0)))
        
        transactions = []
        entity_roles = {
            source_wallet.address: 'source',
            target_wallet.address: 'destination'
        }
        
        current_wallet = source_wallet
        current_time = datetime.now()
        
        # Create intermediary wallets for circular trades
        for i in range(wash_rounds):
            intermediary_addr = f"nft_wash_{i}_{random.randint(10000, 99999)}"
            intermediary = Wallet(
                address=intermediary_addr,
                chain=asset.chain,
                jurisdiction=current_wallet.jurisdiction,
                balance=Decimal("0"),
                created_at=current_time
            )
            entity_roles[intermediary_addr] = f'nft_wash_intermediary_{i}'
            
            # Escalating price (wash trading pattern)
            trade_amount = base_amount * Decimal(1.1) ** i
            
            # Trade to intermediary
            trade_tx_id = f"nft_wash_{i}_a_{random.randint(10000, 99999)}"
            trade_tx = Transaction(
                tx_id=trade_tx_id,
                from_wallet=current_wallet,
                to_wallet=intermediary,
                asset=asset,
                amount=trade_amount,
                fee=Decimal("0.01"),
                timestamp=current_time,
                block_number=0,
                metadata={'motif': 'nft_wash_trading', 'round': i, 'direction': 'forward'}
            )
            transactions.append(trade_tx)
            
            current_time += timedelta(hours=random.uniform(*time_variance))
            current_wallet = intermediary
        
        # Final transfer to target (extracted value)
        final_tx_id = f"nft_wash_final_{random.randint(10000, 99999)}"
        final_amount = base_amount * Decimal(1.1) ** wash_rounds
        final_tx = Transaction(
            tx_id=final_tx_id,
            from_wallet=current_wallet,
            to_wallet=target_wallet,
            asset=asset,
            amount=final_amount,
            fee=Decimal("0.01"),
            timestamp=current_time,
            block_number=0,
            metadata={'motif': 'nft_wash_trading', 'final': True}
        )
        transactions.append(final_tx)
        
        aml_weaknesses = [
            "NFT price manipulation detection gaps",
            "Circular trading pattern recognition",
            "Marketplace correlation weaknesses"
        ]
        
        return transactions, entity_roles, aml_weaknesses


class DormancyCooling(LaunderingMotif):
    """
    Dormancy cooling motif: Adds time delays to reduce suspicion.
    
    Parameters:
        cooling_period_days: Days to wait between phases (default: 30-90)
    """
    
    def generate_subgraph(
        self,
        source_wallet: Wallet,
        target_wallet: Wallet,
        asset: Asset,
        params: Dict
    ) -> Tuple[List[Transaction], Dict[str, str], List[str]]:
        cooling_period_days = params.get('cooling_period_days', (30, 90))
        amount = Decimal(str(params.get('amount', 10.0)))
        
        transactions = []
        entity_roles = {
            source_wallet.address: 'source',
            target_wallet.address: 'destination'
        }
        
        # Create intermediate wallet for cooling
        cooling_addr = f"cooling_{random.randint(10000, 99999)}"
        cooling_wallet = Wallet(
            address=cooling_addr,
            chain=asset.chain,
            jurisdiction=source_wallet.jurisdiction,
            balance=Decimal("0"),
            created_at=datetime.now()
        )
        entity_roles[cooling_addr] = 'cooling_wallet'
        
        # Initial transfer
        initial_tx_id = f"cooling_initial_{random.randint(10000, 99999)}"
        initial_tx = Transaction(
            tx_id=initial_tx_id,
            from_wallet=source_wallet,
            to_wallet=cooling_wallet,
            asset=asset,
            amount=amount,
            fee=Decimal("0.001"),
            timestamp=datetime.now(),
            block_number=0,
            metadata={'motif': 'dormancy_cooling', 'phase': 'deposit'}
        )
        transactions.append(initial_tx)
        
        # Cooling period (dormant)
        cooling_days = random.randint(*cooling_period_days)
        cooled_time = datetime.now() + timedelta(days=cooling_days)
        
        # Transfer after cooling
        cooled_tx_id = f"cooling_exit_{random.randint(10000, 99999)}"
        cooled_tx = Transaction(
            tx_id=cooled_tx_id,
            from_wallet=cooling_wallet,
            to_wallet=target_wallet,
            asset=asset,
            amount=amount,
            fee=Decimal("0.001"),
            timestamp=cooled_time,
            block_number=0,
            metadata={'motif': 'dormancy_cooling', 'phase': 'withdrawal', 'cooling_days': cooling_days}
        )
        transactions.append(cooled_tx)
        
        aml_weaknesses = [
            "Temporal analysis gaps",
            "Dormancy pattern recognition",
            "Long-term correlation weaknesses"
        ]
        
        return transactions, entity_roles, aml_weaknesses


class FalsePositiveTrap(LaunderingMotif):
    """
    False positive trap motif: Generates legitimate patterns that trigger false positives.
    
    Parameters:
        pattern_type: Type of legitimate pattern (default: 'high_frequency_trading')
    """
    
    def generate_subgraph(
        self,
        source_wallet: Wallet,
        target_wallet: Wallet,
        asset: Asset,
        params: Dict
    ) -> Tuple[List[Transaction], Dict[str, str], List[str]]:
        pattern_type = params.get('pattern_type', 'high_frequency_trading')
        amount = Decimal(str(params.get('amount', 10.0)))
        
        transactions = []
        entity_roles = {
            source_wallet.address: 'legitimate_source',
            target_wallet.address: 'legitimate_destination'
        }
        
        if pattern_type == 'high_frequency_trading':
            # High-frequency legitimate trading (looks suspicious but is valid)
            current_time = datetime.now()
            num_trades = 10
            
            for i in range(num_trades):
                trade_tx_id = f"hft_{i}_{random.randint(10000, 99999)}"
                trade_amount = amount / Decimal(num_trades)
                trade_tx = Transaction(
                    tx_id=trade_tx_id,
                    from_wallet=source_wallet if i % 2 == 0 else target_wallet,
                    to_wallet=target_wallet if i % 2 == 0 else source_wallet,
                    asset=asset,
                    amount=trade_amount,
                    fee=Decimal("0.0001"),
                    timestamp=current_time + timedelta(minutes=i * 5),
                    block_number=0,
                    metadata={'motif': 'false_positive_trap', 'pattern': 'hft', 'trade': i}
                )
                transactions.append(trade_tx)
        else:
            # Default: simple legitimate transfer
            tx_id = f"legitimate_{random.randint(10000, 99999)}"
            tx = Transaction(
                tx_id=tx_id,
                from_wallet=source_wallet,
                to_wallet=target_wallet,
                asset=asset,
                amount=amount,
                fee=Decimal("0.001"),
                timestamp=datetime.now(),
                block_number=0,
                metadata={'motif': 'false_positive_trap', 'pattern': 'legitimate_transfer'}
            )
            transactions.append(tx)
        
        aml_weaknesses = [
            "Pattern-based false positive triggers",
            "Legitimate activity misclassification",
            "Context-agnostic rule-based detection"
        ]
        
        return transactions, entity_roles, aml_weaknesses

