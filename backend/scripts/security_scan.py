#!/usr/bin/env python3
"""
Security Scanning Script
اسکریپت برای اسکن امنیتی کد
"""
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


def run_command(cmd: list, description: str) -> dict:
    """Run a command and return results"""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*80)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": ""
        }


def run_bandit():
    """Run Bandit security linter"""
    cmd = [
        "bandit",
        "-r", "app",
        "-f", "json",
        "-o", "security_reports/bandit_report.json"
    ]
    return run_command(cmd, "Bandit Security Linter")


def run_safety():
    """Run Safety dependency vulnerability scanner"""
    cmd = [
        "safety", "check",
        "--json",
        "--output", "security_reports/safety_report.json"
    ]
    return run_command(cmd, "Safety Dependency Scanner")


def run_semgrep():
    """Run Semgrep security scanner"""
    cmd = [
        "semgrep",
        "--config=auto",
        "--json",
        "--output=security_reports/semgrep_report.json",
        "app"
    ]
    return run_command(cmd, "Semgrep Security Scanner")


def generate_report(results: dict):
    """Generate security scan report"""
    report_path = Path("security_reports/security_scan_report.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("NeuroPredict-AI Security Scan Report\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n")
        
        for tool, result in results.items():
            f.write(f"\n{tool.upper()}\n")
            f.write("-" * 80 + "\n")
            f.write(f"Status: {'✓ PASSED' if result['success'] else '✗ FAILED'}\n")
            
            if result.get('stdout'):
                f.write(f"\nOutput:\n{result['stdout']}\n")
            
            if result.get('stderr'):
                f.write(f"\nErrors:\n{result['stderr']}\n")
            
            if result.get('error'):
                f.write(f"\nError: {result['error']}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("Recommendations:\n")
        f.write("1. Review all findings and fix high/critical severity issues\n")
        f.write("2. Update dependencies with known vulnerabilities\n")
        f.write("3. Review code for security best practices\n")
        f.write("4. Run penetration testing for critical findings\n")
        f.write("=" * 80 + "\n")
    
    print(f"\n✓ Security report saved to: {report_path}")


def main():
    print("=" * 80)
    print("NeuroPredict-AI Security Scanning")
    print("=" * 80)
    
    # Check if tools are installed
    tools = {
        "bandit": "pip install bandit[toml]",
        "safety": "pip install safety",
        "semgrep": "pip install semgrep"
    }
    
    missing_tools = []
    for tool, install_cmd in tools.items():
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append((tool, install_cmd))
    
    if missing_tools:
        print("\n⚠️  Missing security tools:")
        for tool, install_cmd in missing_tools:
            print(f"  - {tool}: {install_cmd}")
        print("\nInstall missing tools and run again.")
        return 1
    
    results = {}
    
    # Run security scans
    results['bandit'] = run_bandit()
    results['safety'] = run_safety()
    results['semgrep'] = run_semgrep()
    
    # Generate report
    generate_report(results)
    
    # Summary
    print("\n" + "=" * 80)
    print("Security Scan Summary")
    print("=" * 80)
    
    all_passed = all(r['success'] for r in results.values())
    
    for tool, result in results.items():
        status = "✓ PASSED" if result['success'] else "✗ FAILED"
        print(f"{tool:15} {status}")
    
    if not all_passed:
        print("\n⚠️  Some security scans failed. Please review the reports.")
        return 1
    
    print("\n✓ All security scans passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

