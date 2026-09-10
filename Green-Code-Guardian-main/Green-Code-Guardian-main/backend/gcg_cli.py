#!/usr/bin/env python3
"""
GreenCode Guardian CLI Tool

Usage:
  gcg scan <project-path> --region <region> [--api-url <url>] [--api-key <key>]
  gcg webhook --provider github --url <webhook-url>
  gcg team create --name <name> [--api-key <key>]
  gcg leaderboard [--period week|month|all]
  gcg notify --type carbon --threshold <value>

Examples:
  gcg scan ./my-project --region us-east
  gcg leaderboard --period month
"""

import argparse
import json
import requests
import sys
import os
from datetime import datetime
from pathlib import Path
import subprocess


class GreenCodeGuardianCLI:
    def __init__(self, api_url="http://localhost:8000", api_key=None):
        self.api_url = api_url or os.getenv("GCG_API_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("GCG_API_KEY", "")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }

    def scan_project(self, project_path, region="us-east"):
        """Scan a project directory for sustainability metrics."""
        
        print(f"🔍 Scanning {project_path}...")
        
        # Get basic metrics
        metrics = self._collect_metrics()
        
        # Send to API
        payload = {
            "repo": Path(project_path).name,
            "branch": self._get_git_branch(project_path),
            "commit": self._get_git_commit(project_path),
            "metrics": metrics,
            "carbon_threshold": 75
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/webhook/custom",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Scan submitted!")
            print(f"   Webhook ID: {result.get('webhook_id')}")
            if result.get('alert'):
                print(f"   ⚠️  {result['alert']}")
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to submit scan: {e}")
            return None

    def _collect_metrics(self):
        """Collect system metrics using psutil."""
        try:
            import psutil
            return {
                "cpu": psutil.cpu_percent(interval=1),
                "memory_gb": psutil.virtual_memory().used / (1024**3),
                "disk": psutil.disk_usage('/').percent,
                "execution_time": 0  # Can be measured per-project
            }
        except ImportError:
            print("⚠️  psutil not found. Install with: pip install psutil")
            return {
                "cpu": 0,
                "memory_gb": 0,
                "disk": 0,
                "execution_time": 0
            }

    def _get_git_branch(self, path):
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except:
            return "unknown"

    def _get_git_commit(self, path):
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()[:8]
        except:
            return "unknown"

    def get_leaderboard(self, period="all"):
        """Fetch and display leaderboard."""
        
        try:
            response = requests.get(
                f"{self.api_url}/leaderboard/global",
                params={"period": period, "limit": 10},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            print(f"\n🏆 Global Leaderboard ({data['period']})\n")
            print("Rank | Project                  | Score | Carbon (g)")
            print("-" * 55)
            
            for entry in data.get('leaderboard', []):
                rank = entry['rank']
                project = entry['project'][:20].ljust(20)
                score = f"{entry['green_score']:.1f}".ljust(5)
                carbon = f"{entry['carbon_emissions']:.1f}".ljust(9)
                print(f" {rank:2d}  | {project} | {score} | {carbon}")
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch leaderboard: {e}")
            return None

    def get_trending(self, period="week"):
        """Get trending projects."""
        
        try:
            response = requests.get(
                f"{self.api_url}/leaderboard/trending",
                params={"period": period},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            print(f"\n📈 Trending Projects ({period})\n")
            
            for project in data.get('trending', []):
                trend_arrow = "📈" if project['improvement'] >= 0 else "📉"
                print(f"{trend_arrow} {project['project']}")
                print(f"   Score: {project['previous_score']:.1f} → {project['current_score']:.1f} ({project['improvement_percent']:+.1f}%)")
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch trending: {e}")
            return None

    def get_user_stats(self, user_id):
        """Get user statistics."""
        
        try:
            response = requests.get(
                f"{self.api_url}/leaderboard/user/{user_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            print(f"\n👤 Stats for {data['name']}\n")
            print(f"Total Scans: {data['total_scans']}")
            print(f"Avg Green Score: {data['avg_green_score']:.1f}")
            print(f"Carbon Saved: {data['total_carbon_saved']:.1f}g")
            
            if data['achievements']:
                print(f"Achievements: {', '.join(data['achievements'])}")
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch user stats: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="GreenCode Guardian CLI - Sustainability monitoring for your code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan project for sustainability metrics")
    scan_parser.add_argument("project_path", help="Path to project directory")
    scan_parser.add_argument("--region", default="us-east", help="Region for carbon calculation")
    scan_parser.add_argument("--api-url", help="GreenCode Guardian API URL")
    scan_parser.add_argument("--api-key", help="API key for authentication")
    
    # Leaderboard command
    board_parser = subparsers.add_parser("leaderboard", help="View global leaderboard")
    board_parser.add_argument("--period", default="all", choices=["week", "month", "all"])
    board_parser.add_argument("--api-url", help="GreenCode Guardian API URL")
    
    # Trending command
    trending_parser = subparsers.add_parser("trending", help="View trending projects")
    trending_parser.add_argument("--period", default="week", choices=["week", "month"])
    trending_parser.add_argument("--api-url", help="GreenCode Guardian API URL")
    
    # User stats command
    stats_parser = subparsers.add_parser("stats", help="View user statistics")
    stats_parser.add_argument("user_id", help="User ID")
    stats_parser.add_argument("--api-url", help="GreenCode Guardian API URL")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    api_url = args.api_url if hasattr(args, 'api_url') and args.api_url else None
    api_key = args.api_key if hasattr(args, 'api_key') and args.api_key else None
    
    cli = GreenCodeGuardianCLI(api_url=api_url, api_key=api_key)
    
    if args.command == "scan":
        cli.scan_project(args.project_path, args.region)
    elif args.command == "leaderboard":
        cli.get_leaderboard(args.period)
    elif args.command == "trending":
        cli.get_trending(args.period)
    elif args.command == "stats":
        cli.get_user_stats(args.user_id)


if __name__ == "__main__":
    main()
