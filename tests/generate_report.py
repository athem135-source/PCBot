"""
PDBOT 300-Question Test Report Generator
=========================================
Generates a comprehensive markdown report from test results.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, 'results')
REPORTS_DIR = os.path.join(SCRIPT_DIR, 'reports')

def load_latest_results() -> Optional[Tuple[Dict[str, Any], str]]:
    """Load the most recent test results file"""
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    files = [f for f in os.listdir(RESULTS_DIR) if f.startswith('test_results_') and f.endswith('.json')]
    if not files:
        return None
    latest = sorted(files, reverse=True)[0]
    filepath = os.path.join(RESULTS_DIR, latest)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f), latest

def generate_report() -> Optional[str]:
    """Generate comprehensive markdown report"""
    result = load_latest_results()
    if result is None:
        print("No test results found!")
        return
    
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
    report.append("# 📊 PDBOT 300-Question Comprehensive Test Report\n")
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
    
    report.append("| Metric | Value |\n")
    report.append("|--------|-------|\n")
    report.append(f"| **Total Questions** | {total} |\n")
    report.append(f"| **Passed** | {passed} ({rate:.1f}%) |\n")
    report.append(f"| **Failed** | {failed} ({100-rate:.1f}%) |\n")
    report.append(f"| **Overall Accuracy** | {rate:.1f}% |\n")
    report.append(f"| **Avg Response Time** | {avg_time:.2f}s |\n")
    report.append(f"| **Total Test Duration** | {avg_time * total / 60:.1f} min |\n")
    report.append("\n")
    
    # Overall Grade
    if rate >= 95:
        grade = "A+"
        grade_desc = "Excellent"
    elif rate >= 90:
        grade = "A"
        grade_desc = "Very Good"
    elif rate >= 85:
        grade = "B+"
        grade_desc = "Good"
    elif rate >= 80:
        grade = "B"
        grade_desc = "Satisfactory"
    elif rate >= 70:
        grade = "C"
        grade_desc = "Needs Improvement"
    else:
        grade = "D"
        grade_desc = "Poor"
    
    report.append(f"### 🏆 Overall Grade: **{grade}** ({grade_desc})\n\n")
    
    # Category Breakdown
    report.append("---\n\n## 📈 Category Breakdown\n\n")
    report.append("| Category | Total | Passed | Failed | Accuracy | Avg Time | Status |\n")
    report.append("|----------|-------|--------|--------|----------|----------|--------|\n")
    
    category_order = [
        'inscope_detailed', 'inscope_short', 'numeric_financial',
        'trap_questions', 'trick_questions', 'redline_abuse',
        'offscope', 'ambiguous_greetings', 'manual_sections'
    ]
    
    category_names = {
        'inscope_detailed': 'In-Scope Detailed',
        'inscope_short': 'In-Scope Short',
        'numeric_financial': 'Numeric/Financial',
        'trap_questions': 'Trap Questions',
        'trick_questions': 'Trick Questions',
        'redline_abuse': 'Red-Line/Abuse',
        'offscope': 'Off-Scope',
        'ambiguous_greetings': 'Greetings/Ambiguous',
        'manual_sections': 'Manual Sections'
    }
    
    for cat in category_order:
        if cat in categories:
            c = categories[cat]
            acc = (c['passed'] / c['total'] * 100) if c['total'] > 0 else 0
            avg = c['total_time'] / c['total'] if c['total'] > 0 else 0
            status = "✅" if acc >= 90 else "⚠️" if acc >= 70 else "❌"
            name = category_names.get(cat, cat)
            report.append(f"| {name} | {c['total']} | {c['passed']} | {c['failed']} | {acc:.1f}% | {avg:.2f}s | {status} |\n")
    
    report.append("\n")
    
    # Detailed Metrics
    report.append("---\n\n## 📊 Detailed Metrics\n\n")
    
    # Response Time Analysis
    times = [r.get('response_time', 0) for r in results]
    report.append("### ⏱️ Response Time Analysis\n\n")
    report.append("| Metric | Value |\n")
    report.append("|--------|-------|\n")
    report.append(f"| Minimum | {min(times):.2f}s |\n")
    report.append(f"| Maximum | {max(times):.2f}s |\n")
    report.append(f"| Average | {sum(times)/len(times):.2f}s |\n")
    report.append(f"| Median | {sorted(times)[len(times)//2]:.2f}s |\n")
    fast = len([t for t in times if t < 3])
    medium = len([t for t in times if 3 <= t < 6])
    slow = len([t for t in times if t >= 6])
    report.append(f"| Fast (<3s) | {fast} ({fast/len(times)*100:.1f}%) |\n")
    report.append(f"| Medium (3-6s) | {medium} ({medium/len(times)*100:.1f}%) |\n")
    report.append(f"| Slow (>6s) | {slow} ({slow/len(times)*100:.1f}%) |\n")
    report.append("\n")
    
    # Citation Analysis
    with_sources = len([r for r in results if r.get('sources')])
    report.append("### 📚 Citation Analysis\n\n")
    report.append("| Metric | Value |\n")
    report.append("|--------|-------|\n")
    report.append(f"| Responses with Citations | {with_sources} ({with_sources/len(results)*100:.1f}%) |\n")
    report.append(f"| Responses without Citations | {len(results) - with_sources} |\n")
    
    # Page reference distribution
    pages = []
    for r in results:
        for s in r.get('sources', []):
            pages.append(s.get('page', 0))
    if pages:
        report.append(f"| Unique Pages Referenced | {len(set(pages))} |\n")
        report.append(f"| Most Referenced Page | {max(set(pages), key=pages.count)} |\n")
    report.append("\n")
    
    # Issues Found
    report.append("---\n\n## 🚨 Issues Found\n\n")
    
    all_issues = []
    for cat in category_order:
        if cat in categories and categories[cat]['issues']:
            for issue in categories[cat]['issues']:
                all_issues.append({
                    'category': category_names.get(cat, cat),
                    'question': issue['question'],
                    'answer': issue['answer'][:200] if issue.get('answer') else 'N/A',
                    'issues': issue.get('issues', [])
                })
    
    if all_issues:
        report.append(f"**Total Issues:** {len(all_issues)}\n\n")
        for i, issue in enumerate(all_issues, 1):
            report.append(f"### Issue #{i}: {issue['category']}\n\n")
            report.append(f"**Question:** {issue['question']}\n\n")
            report.append(f"**Answer (truncated):** {issue['answer']}...\n\n")
            if issue['issues']:
                report.append(f"**Problems:** {', '.join(issue['issues'])}\n\n")
            report.append("---\n\n")
    else:
        report.append("✅ **No critical issues found!**\n\n")
    
    # Full Q&A Log (Collapsible)
    report.append("---\n\n## 📝 Complete Question & Answer Log\n\n")
    
    for cat in category_order:
        if cat in categories:
            name = category_names.get(cat, cat)
            c = categories[cat]
            acc = (c['passed'] / c['total'] * 100) if c['total'] > 0 else 0
            
            report.append(f"<details>\n<summary><b>{name}</b> ({c['total']} questions, {acc:.1f}% accuracy)</summary>\n\n")
            report.append("| # | Question | Answer (truncated) | Time | Sources | Status |\n")
            report.append("|---|----------|-------------------|------|---------|--------|\n")
            
            for i, q in enumerate(c['questions'], 1):
                question = q['question'][:40] + "..." if len(q['question']) > 40 else q['question']
                answer = q.get('answer', 'N/A')[:50] + "..." if len(q.get('answer', '')) > 50 else q.get('answer', 'N/A')
                answer = answer.replace('\n', ' ').replace('|', '\\|')
                time = q.get('response_time', 0)
                sources = len(q.get('sources', []))
                status = "✅" if q['passed'] else "❌"
                report.append(f"| {i} | {question} | {answer} | {time:.1f}s | {sources} | {status} |\n")
            
            report.append("\n</details>\n\n")
    
    # Recommendations
    report.append("---\n\n## 💡 Recommendations\n\n")
    
    recs = []
    for cat in category_order:
        if cat in categories:
            c = categories[cat]
            acc = (c['passed'] / c['total'] * 100) if c['total'] > 0 else 0
            if acc < 90:
                name = category_names.get(cat, cat)
                recs.append(f"- **{name}** ({acc:.1f}%): Review and improve detection/response patterns")
    
    if recs:
        report.append("### Areas Needing Improvement:\n\n")
        report.append("\n".join(recs))
        report.append("\n\n")
    else:
        report.append("✅ All categories performing at 90%+ accuracy. System is production-ready.\n\n")
    
    # Footer
    report.append("---\n\n")
    report.append("*Report generated by PDBOT 300-Question Test Suite*\n")
    report.append(f"*Test conducted on: {data.get('timestamp', 'N/A')}*\n")
    
    # Write report
    report_text = "".join(report)
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    report_filename = os.path.join(REPORTS_DIR, f"TEST_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"Report generated: {report_filename}")
    print(f"\nQuick Summary:")
    print(f"  Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"  Accuracy: {rate:.1f}% | Grade: {grade}")
    
    return report_text

if __name__ == "__main__":
    generate_report()
