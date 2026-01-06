# -*- coding: utf-8 -*-
"""
Narrative Engine

Generates human-readable plain-English narratives explaining each scenario:
- What the scenario represents
- Step-by-step transaction flow
- Why legacy AML systems fail
- What signals AIML should detect
"""

from typing import List
from .scenario import Scenario, ScenarioIntent


def generate_narrative(scenario: Scenario) -> str:
    """
    Generate plain-English markdown narrative for a scenario.
    
    Args:
        scenario: Scenario object to narrate
    
    Returns:
        Markdown-formatted narrative string
    """
    lines = []
    
    # Header
    lines.append("# Scenario Narrative")
    lines.append("")
    lines.append(f"**Scenario ID:** `{scenario.scenario_id}`")
    lines.append(f"**Intent:** {scenario.intent.value}")
    lines.append(f"**Created:** {scenario.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Overview
    lines.append("## Overview")
    lines.append("")
    lines.append(_get_overview(scenario))
    lines.append("")
    
    # Transaction Flow
    lines.append("## Transaction Flow")
    lines.append("")
    lines.append(_get_transaction_flow(scenario))
    lines.append("")
    
    # Why Legacy AML Fails
    lines.append("## Why Legacy AML Systems Fail")
    lines.append("")
    lines.append(_get_legacy_failures(scenario))
    lines.append("")
    
    # AIML Signals
    lines.append("## Signals AIML Should Detect")
    lines.append("")
    lines.append(_get_aiml_signals(scenario))
    lines.append("")
    
    # Risk Indicators
    lines.append("## Risk Indicators")
    lines.append("")
    risk_summary = scenario.get_risk_summary()
    lines.append(f"- **Total Transactions:** {risk_summary['total_transactions']}")
    lines.append(f"- **Entities Involved:** {risk_summary['entities_involved']}")
    lines.append(f"- **Time Span:** {risk_summary['time_span_days']} days")
    lines.append(f"- **Total Amount:** {risk_summary['total_amount']} {risk_summary['unique_assets'][0] if risk_summary['unique_assets'] else 'N/A'}")
    lines.append(f"- **Chains Used:** {', '.join(risk_summary['unique_chains'])}")
    lines.append(f"- **AML Weaknesses Identified:** {risk_summary['aml_weaknesses_count']}")
    lines.append("")
    
    # Integrity
    lines.append("---")
    lines.append("")
    lines.append(f"**Scenario Integrity Hash:** `{scenario.scenario_hash}`")
    lines.append("")
    lines.append("*This is ARTIFICIAL data generated for demo and evaluation purposes only.*")
    
    return "\n".join(lines)


def _get_overview(scenario: Scenario) -> str:
    """Generate overview section based on intent and motifs"""
    intent_descriptions = {
        ScenarioIntent.LAUNDERING: "This scenario demonstrates a money laundering operation designed to obscure the origin of illicit funds through multiple transaction layers and jurisdictional arbitrage.",
        ScenarioIntent.SANCTIONS_EVASION: "This scenario demonstrates sanctions evasion through cross-chain transfers and jurisdiction hopping to circumvent regulatory restrictions.",
        ScenarioIntent.RANSOMWARE_LIQUIDATION: "This scenario demonstrates ransomware fund liquidation through mixing services and time delays to obscure the source of funds.",
        ScenarioIntent.FALSE_POSITIVE_TRAP: "This scenario demonstrates legitimate trading activity that may trigger false positive alerts in rule-based AML systems.",
        ScenarioIntent.TAX_EVASION: "This scenario demonstrates tax evasion patterns through obfuscated transaction flows."
    }
    
    base_description = intent_descriptions.get(scenario.intent, "This scenario demonstrates an adversarial AML pattern.")
    
    motifs_desc = []
    if 'CrossChainBridge' in scenario.motifs_used:
        motifs_desc.append("cross-chain bridging")
    if 'MixerObfuscation' in scenario.motifs_used:
        motifs_desc.append("mixer services")
    if 'PeelChain' in scenario.motifs_used:
        motifs_desc.append("peel chains")
    if 'NFTWashTrading' in scenario.motifs_used:
        motifs_desc.append("NFT wash trading")
    if 'DormancyCooling' in scenario.motifs_used:
        motifs_desc.append("dormancy periods")
    
    if motifs_desc:
        techniques = ", ".join(motifs_desc)
        return f"{base_description} The scenario employs {techniques} to achieve its objective."
    
    return base_description


def _get_transaction_flow(scenario: Scenario) -> str:
    """Generate step-by-step transaction flow description"""
    lines = []
    
    transactions = []
    for from_addr, to_addr, data in scenario.transaction_graph.edges(data=True):
        tx = data['transaction']
        transactions.append((tx.timestamp, tx, from_addr, to_addr))
    
    transactions.sort(key=lambda x: x[0])
    
    lines.append("The transaction flow proceeds as follows:")
    lines.append("")
    
    for i, (timestamp, tx, from_addr, to_addr) in enumerate(transactions[:20], 1):  # Limit to first 20 for readability
        from_role = scenario.entity_roles.get(from_addr, 'unknown')
        to_role = scenario.entity_roles.get(to_addr, 'unknown')
        
        lines.append(f"{i}. **Transaction {tx.tx_id[:12]}...** ({timestamp.strftime('%Y-%m-%d %H:%M')})")
        lines.append(f"   - From: `{from_addr[:20]}...` ({from_role})")
        lines.append(f"   - To: `{to_addr[:20]}...` ({to_role})")
        lines.append(f"   - Amount: {tx.amount} {tx.asset.symbol}")
        lines.append("")
    
    if len(transactions) > 20:
        lines.append(f"*... and {len(transactions) - 20} more transactions*")
        lines.append("")
    
    return "\n".join(lines)


def _get_legacy_failures(scenario: Scenario) -> str:
    """Explain why legacy AML systems fail"""
    lines = []
    
    lines.append("Legacy rule-based AML systems fail to detect this scenario due to:")
    lines.append("")
    
    for weakness in scenario.aml_weaknesses:
        lines.append(f"- **{weakness}**: Traditional systems lack the capability to correlate patterns across these dimensions, allowing the adversarial behavior to go undetected.")
    
    lines.append("")
    lines.append("Specific failure modes include:")
    lines.append("")
    
    if 'CrossChainBridge' in scenario.motifs_used:
        lines.append("- **Cross-chain analysis gaps**: Legacy systems typically monitor single chains and cannot correlate activity across multiple blockchains.")
    
    if 'MixerObfuscation' in scenario.motifs_used:
        lines.append("- **Mixer exit correlation**: Mixing services break transaction links, making it difficult for rule-based systems to trace fund flows.")
    
    if 'PeelChain' in scenario.motifs_used:
        lines.append("- **Small amount thresholds**: Breaking large amounts into smaller transactions allows actors to stay below rule-based thresholds.")
    
    if 'DormancyCooling' in scenario.motifs_used:
        lines.append("- **Temporal analysis limitations**: Long dormancy periods fall outside typical rule-based time windows, causing systems to lose context.")
    
    if scenario.intent == ScenarioIntent.FALSE_POSITIVE_TRAP:
        lines.append("- **Context-agnostic rules**: Legitimate high-frequency trading patterns may trigger false positives due to lack of contextual understanding.")
    
    return "\n".join(lines)


def _get_aiml_signals(scenario: Scenario) -> str:
    """Describe signals that AIML systems should detect"""
    lines = []
    
    lines.append("Advanced AIML systems should detect the following signals:")
    lines.append("")
    
    risk_summary = scenario.get_risk_summary()
    
    if risk_summary['total_transactions'] > 10:
        lines.append("- **High transaction velocity**: Unusual frequency of transactions relative to entity behavior patterns")
    
    if len(risk_summary['unique_chains']) > 1:
        lines.append("- **Cross-chain patterns**: Correlation of wallet addresses across multiple blockchains")
    
    if risk_summary['time_span_days'] > 30:
        lines.append("- **Extended time windows**: Transactions spanning extended periods with suspicious patterns")
    
    if 'MixerObfuscation' in scenario.motifs_used:
        lines.append("- **Mixer service interactions**: Known mixer service wallet addresses in transaction graph")
    
    if 'PeelChain' in scenario.motifs_used:
        lines.append("- **Structured transaction patterns**: Systematic breakdown of amounts into smaller increments")
    
    if scenario.intent == ScenarioIntent.SANCTIONS_EVASION:
        lines.append("- **Jurisdiction hopping**: Rapid movement across jurisdictions with different regulatory tiers")
        lines.append("- **Sanctioned entity patterns**: Wallet addresses associated with known sanctioned entities or jurisdictions")
    
    if scenario.intent == ScenarioIntent.RANSOMWARE_LIQUIDATION:
        lines.append("- **Ransomware wallet patterns**: Source addresses matching known ransomware payment patterns")
        lines.append("- **Rapid liquidation timing**: Unusual timing patterns relative to known ransomware events")
    
    lines.append("")
    lines.append("These signals require graph-based analysis, temporal pattern recognition, and cross-chain correlation capabilities that go beyond traditional rule-based systems.")
    
    return "\n".join(lines)

