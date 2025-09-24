#!/usr/bin/env python3
"""
Background Test Runner for HackReality Bot
Runs tests automatically and reports results
"""
import os
import sys
import subprocess
import time
import json
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackgroundTestRunner:
    """Runs tests in the background and manages results"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results_file = self.project_root / "test_results.json"
        self.last_run_file = self.project_root / "last_test_run.txt"
        self.test_log_file = self.project_root / "test_run.log"
        
    def run_tests(self):
        """Run the test suite and return results"""
        logger.info("🧪 Starting automated test run...")
        
        start_time = datetime.now()
        
        try:
            # Change to project directory
            os.chdir(self.project_root)
            
            # Run tests with coverage
            cmd = [
                sys.executable, "-m", "pytest", 
                "tests/", 
                "-v", 
                "--tb=short",
                "--cov=modules", 
                "--cov=main", 
                "--cov-report=json:coverage.json",
                "--cov-report=html:htmlcov",
                "--junitxml=test_results.xml"
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            # Run tests and capture output
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Parse results
            test_results = {
                "timestamp": start_time.isoformat(),
                "duration_seconds": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "test_count": self._parse_test_count(result.stdout),
                "failure_count": self._parse_failure_count(result.stdout)
            }
            
            # Save results
            self._save_results(test_results)
            
            # Log results
            if test_results["success"]:
                logger.info(f"✅ Tests PASSED in {duration:.2f}s - {test_results['test_count']} tests")
            else:
                logger.error(f"❌ Tests FAILED in {duration:.2f}s - {test_results['failure_count']} failures")
                logger.error(f"Error output: {result.stderr}")
            
            return test_results
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Test run timed out after 5 minutes")
            return {
                "timestamp": start_time.isoformat(),
                "duration_seconds": 300,
                "return_code": -1,
                "stdout": "",
                "stderr": "Test run timed out",
                "success": False,
                "test_count": 0,
                "failure_count": 0
            }
        except Exception as e:
            logger.error(f"❌ Error running tests: {e}")
            return {
                "timestamp": start_time.isoformat(),
                "duration_seconds": 0,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False,
                "test_count": 0,
                "failure_count": 0
            }
    
    def _parse_test_count(self, output):
        """Parse number of tests from pytest output"""
        try:
            lines = output.split('\n')
            for line in lines:
                if "passed" in line and "failed" in line:
                    # Extract number before "passed"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            return int(parts[i-1])
        except:
            pass
        return 0
    
    def _parse_failure_count(self, output):
        """Parse number of failures from pytest output"""
        try:
            lines = output.split('\n')
            for line in lines:
                if "failed" in line and "passed" in line:
                    # Extract number before "failed"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "failed":
                            return int(parts[i-1])
        except:
            pass
        return 0
    
    def _save_results(self, results):
        """Save test results to file"""
        try:
            # Save JSON results
            with open(self.results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Save timestamp of last run
            with open(self.last_run_file, 'w') as f:
                f.write(results["timestamp"])
            
            logger.info(f"📊 Test results saved to {self.results_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def get_last_results(self):
        """Get the last test results"""
        try:
            if self.results_file.exists():
                with open(self.results_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading results: {e}")
        return None
    
    def run_continuously(self, interval_minutes=30):
        """Run tests continuously at specified intervals"""
        logger.info(f"🔄 Starting continuous test runs every {interval_minutes} minutes...")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                logger.info("⏰ Starting scheduled test run...")
                results = self.run_tests()
                
                if not results["success"]:
                    logger.warning("⚠️  Tests failed - consider investigating")
                
                # Wait for next run
                logger.info(f"😴 Sleeping for {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("🛑 Continuous testing stopped by user")
        except Exception as e:
            logger.error(f"❌ Error in continuous testing: {e}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Background Test Runner for HackReality Bot")
    parser.add_argument("--continuous", action="store_true", 
                       help="Run tests continuously")
    parser.add_argument("--interval", type=int, default=30,
                       help="Interval in minutes for continuous runs (default: 30)")
    parser.add_argument("--once", action="store_true",
                       help="Run tests once and exit")
    
    args = parser.parse_args()
    
    runner = BackgroundTestRunner()
    
    if args.continuous:
        runner.run_continuously(args.interval)
    else:
        # Default: run once
        results = runner.run_tests()
        if not results["success"]:
            sys.exit(1)

if __name__ == "__main__":
    main()
