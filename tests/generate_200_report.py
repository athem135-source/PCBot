"""
PDBOT 200-Question Test Report Generator
=========================================
Generates detailed markdown analysis report.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, 'results')
REPORTS_DIR = os.path.join(SCRIPT_DIR, 'reports')


def load_latest_200_results() -> Optional[Tuple[Dict[str, Any], str]]:
    """Load the most recent 200-question test results file"""
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    files = [f for f in os.listdir(RESULTS_DIR) if f.startswith('test_200_') and f.endswith('.json')]
    if not files:
        return None
    latest = sorted(files, reverse=True)[0]
    filepath = os.path.join(RESULTS_DIR, latest)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f), latest


def generate_200_report() -> Optional[str]:
    """Generate comprehensive markdown report for 200-question test"""
    result = load_latest_200_results()
    if result is None:
        print("No test results found!")
        return None
    
    data, filename = result
    results = data['detailed_results']
    
    # Category stats with explicit types
    categories: Dict[str, Dict[str, Any]] = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = {
                'total': 0, 'passed': 0, 'failed': 0,
                'total_time': 0.0, 'questions': [], 'issues': []
            }
        categories[cat]['total'] += 1
        categories[cat]['total_time'] += r.get('response_time', 0)
        categories[cat]['questions'].append(r)
        if r['passed']:
            categories[cat]['passed'] += 1
        else:
            categories[cat]['failed'] += 1
            categories[cat]['issues'].append(r)
    
    # Build report
    report = []
    report.append("# 📊 PDBOT 200-Question Comprehensive Test Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Source File:** `{filename}`\n")
    report.append("\n---\n")
    
    # Executive Summary
    report.append("## 📋 Executive Summary\n")
    total = data['total_questions']
    passed = data['total_passed']
    failed = data['total_failed']
    rate = data['pass_rate']
    avg_time = data['avg_response_time']
    
    # Grade calculation
    if rate >= 95:
        grade = "A+"
    elif rate >= 90:
        grade = "A"
    elif rate >= 85:
        grade = "B+"
    elif rate >= 80:
        grade = "B"
    elif rate >= 75:
        grade = "C+"
    elif rate >= 70:
        grade = "C"
    else:
        grade = "D"
    
    report.append(f"| Metric | Value |\n")
    report.append(f"|--------|-------|\n")
    report.append(f"| **Total Questions** | {total} |\n")
    report.append(f"| **Passed** | {passed} ({rate:.1f}%) |\n")
    report.append(f"| **Failed** | {failed} ({100-rate:.1f}%) |\n")
    report.append(f"| **Average Response Time** | {avg_time:.2f}s |\n")
    report.append(f"| **Overall Grade** | **{grade}** |\n")
    report.append("\n")
    
    # Category Breakdown
    report.append("## 📈 Category Breakdown\n\n")
    report.append("| Category | Pass | Fail | Accuracy | Status |\n")
    report.append("|----------|------|------|----------|--------|\n")
    
    category_order = [
        'inscope_detailed', 'inscope_short', 'definitions', 'comparisons',
        'numeric_budget', 'procedures', 'offscope_sports', 'offscope_medical',
        'offscope_entertainment', 'offscope_recipes', 'offscope_general',
        'abuse_english', 'abuse_urdu', 'redline_bribery', 'redline_corruption',
        'redline_misuse', 'greetings'
    ]
    
    for cat in category_order:
        if cat in categories:
            c = categories[cat]
            acc = (c['passed'] / c['total'] * 100) if c['total'] > 0 else 0
            status = "✅" if acc == 100 else "⚠️" if acc >= 80 else "❌"
            report.append(f"| {cat} | {c['passed']} | {c['failed']} | {acc:.1f}% | {status} |\n")
    
    report.append("\n")
    
    # Detailed Issues Analysis
    report.append("## 🔍 Detailed Issues Analysis\n\n")
    
    # Group issues by type
    issue_types = {
        'comparison_issues': [],
        'offscope_failures': [],
        'redline_concerns': [],
        'abuse_misses': [],
        'procedure_issues': [],
        'other_issues': []
    }
    
    for r in results:
        if not r['passed']:
            if r['category'] == 'comparisons':
                issue_types['comparison_issues'].append(r)
            elif r['category'].startswith('offscope'):
                issue_types['offscope_failures'].append(r)
            elif r['category'].startswith('redline'):
                issue_types['redline_concerns'].append(r)
            elif r['category'].startswith('abuse'):
                issue_types['abuse_misses'].append(r)
            elif r['category'] == 'procedures':
                issue_types['procedure_issues'].append(r)
            else:
                issue_types['other_issues'].append(r)
    
    # Comparison Issues
    if issue_types['comparison_issues']:
        report.append("### 📊 Comparison Query Issues\n\n")
        report.append("These queries asked for comparisons but the response validation flagged them:\n\n")
        for r in issue_types['comparison_issues']:
            report.append(f"**Q:** {r['question']}\n\n")
            report.append(f"**Response Preview:**\n> {r['answer_preview'][:300]}...\n\n")
            report.append(f"**Analysis:** Response appears to provide comparison but may lack explicit comparison language (however, whereas, on the other hand, etc.)\n\n")
            report.append("---\n\n")
    
    # Off-scope Failures
    if issue_types['offscope_failures']:
        report.append("### 🚫 Off-Scope Detection Issues\n\n")
        report.append("These off-topic queries were not properly declined:\n\n")
        
        # Group by subcategory
        by_type = {}
        for r in issue_types['offscope_failures']:
            cat = r['category'].replace('offscope_', '')
            if cat not in by_type:
                by_type[cat] = []
            by_type[cat].append(r)
        
        for cat_type, items in by_type.items():
            report.append(f"#### {cat_type.title()} ({len(items)} issues)\n\n")
            for r in items[:5]:  # Show first 5
                report.append(f"- **Q:** {r['question']}\n")
                response_start = r['answer_preview'][:150].replace('\n', ' ')
                report.append(f"  - Response: `{response_start}...`\n")
            if len(items) > 5:
                report.append(f"  - *...and {len(items)-5} more*\n")
            report.append("\n")
    
    # Red-line Concerns (CRITICAL)
    if issue_types['redline_concerns']:
        report.append("### 🚨 RED-LINE SAFETY CONCERNS (CRITICAL)\n\n")
        report.append("⚠️ **These queries should have been firmly declined but were not:**\n\n")
        for r in issue_types['redline_concerns']:
            report.append(f"**Q:** {r['question']}\n\n")
            report.append(f"**Full Response:**\n```\n{r['answer_preview']}\n```\n\n")
            report.append(f"**Risk Level:** 🔴 HIGH - May provide harmful guidance\n\n")
            report.append("---\n\n")
    
    # Abuse Detection Misses
    if issue_types['abuse_misses']:
        report.append("### 🛡️ Abuse Detection Misses\n\n")
        for r in issue_types['abuse_misses']:
            report.append(f"- **Input:** `{r['question']}`\n")
            report.append(f"  - Response: {r['answer_preview'][:100]}...\n\n")
    
    # Procedure Issues
    if issue_types['procedure_issues']:
        report.append("### 📝 Procedure Query Issues\n\n")
        for r in issue_types['procedure_issues']:
            report.append(f"**Q:** {r['question']}\n\n")
            report.append(f"**Response:** {r['answer_preview'][:300]}...\n\n")
            report.append("**Issue:** Response lacks step-by-step structure\n\n")
    
    # Recommendations
    report.append("## 💡 Recommendations\n\n")
    
    recommendations = []
    
    if issue_types['redline_concerns']:
        recommendations.append("1. **🚨 CRITICAL: Enhance red-line detection patterns** - Add patterns for 'divert funds', 'award contracts to relatives', etc.")
    
    if issue_types['offscope_failures']:
        recommendations.append("2. **Improve off-scope response format** - Ensure consistent 'I can only help with PND Manual questions' response")
    
    if issue_types['comparison_issues']:
        recommendations.append("3. **Review comparison validation** - Current validation may be too strict; responses are providing valid comparisons")
    
    if issue_types['abuse_misses']:
        recommendations.append("4. **Fix abuse pattern order** - Pattern `you're an idiot` not caught due to word order in regex")
    
    if not recommendations:
        recommendations.append("✅ All categories performing well!")
    
    for rec in recommendations:
        report.append(f"{rec}\n\n")
    
    # Full Q&A Log
    report.append("## 📝 Full Test Log\n\n")
    report.append("<details>\n<summary><b>Click to expand all 200 Q&A pairs</b></summary>\n\n")
    
    for cat in category_order:
        if cat in categories:
            report.append(f"### {cat.upper()}\n\n")
            for i, q in enumerate(categories[cat]['questions'], 1):
                status = "✅" if q['passed'] else "❌"
                report.append(f"**{i}. {status}** {q['question']}\n\n")
                report.append(f"> {q['answer_preview'][:200]}...\n\n")
    
    report.append("</details>\n\n")
    
    # Footer
    report.append("---\n\n")
    report.append(f"*Report generated by PDBOT Test Suite v3.3.6*\n")
    report.append(f"*Test conducted on: {data.get('timestamp', 'N/A')}*\n")
    
    # Write report
    report_text = "".join(report)
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    report_filename = os.path.join(REPORTS_DIR, f"TEST_200_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"Report generated: {report_filename}")
    print(f"\nQuick Summary:")
    print(f"  Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"  Accuracy: {rate:.1f}% | Grade: {grade}")
    
    return report_text


if __name__ == "__main__":
    generate_200_report()
