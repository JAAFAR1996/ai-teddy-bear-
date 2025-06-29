#!/usr/bin/env python3
"""
Chaos Engineering Experiment Runner
SRE Team Implementation - Task 15
Comprehensive chaos experiment execution and management
"""

import asyncio
import argparse
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import chaos modules
sys.path.append(str(Path(__file__).parent.parent))

from chaos.experiments.child_safety_chaos import ChildSafetyChaosExperiment, create_child_safety_chaos_experiment
from chaos.infrastructure.chaos_orchestrator import ChaosOrchestrator, FailureType, ExperimentStatus
from chaos.monitoring.chaos_metrics import ChaosMetricsCollector
from chaos.actions.safety import inject_toxic_content, test_parental_controls_bypass
from chaos.actions.ai import trigger_hallucination, test_bias_detection
from chaos.actions.recovery import restore_all_systems, validate_system_recovery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChaosExperimentRunner:
    """Main chaos experiment runner"""
    
    def __init__(self):
        self.orchestrator = ChaosOrchestrator()
        self.metrics_collector = ChaosMetricsCollector()
        self.experiment_results = {}
        
    async def run_child_safety_experiment(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run comprehensive child safety chaos experiment"""
        
        logger.info("🧸 Starting Child Safety Chaos Experiment")
        
        experiment_id = f"child_safety_{int(time.time())}"
        start_time = datetime.now()
        
        try:
            # Initialize experiment
            experiment = ChildSafetyChaosExperiment(config)
            chaos_spec = experiment.create_child_safety_chaos_experiment()
            
            # Start metrics collection
            metrics_task = asyncio.create_task(
                self.metrics_collector.start_monitoring(experiment_id, 600)  # 10 minutes
            )
            
            results = {
                "experiment_id": experiment_id,
                "start_time": start_time.isoformat(),
                "experiment_type": "child_safety",
                "phases": {}
            }
            
            # Phase 1: Baseline Health Check
            logger.info("📊 Phase 1: Baseline Health Check")
            baseline_health = await self._check_system_health()
            results["phases"]["baseline_health"] = baseline_health
            
            if not baseline_health["all_healthy"]:
                logger.error("❌ System not healthy, aborting experiment")
                results["status"] = "aborted"
                results["reason"] = "System not healthy"
                return results
            
            # Phase 2: Safety System Testing
            logger.info("🛡️ Phase 2: Safety System Testing")
            safety_results = await self._run_safety_tests()
            results["phases"]["safety_tests"] = safety_results
            
            # Phase 3: AI Safety Testing
            logger.info("🧠 Phase 3: AI Safety Testing")
            ai_safety_results = await self._run_ai_safety_tests()
            results["phases"]["ai_safety_tests"] = ai_safety_results
            
            # Phase 4: Failure Injection
            logger.info("💥 Phase 4: Failure Injection")
            failure_results = await self._inject_controlled_failures(experiment_id)
            results["phases"]["failure_injection"] = failure_results
            
            # Phase 5: Recovery Validation
            logger.info("🔄 Phase 5: Recovery Validation")
            recovery_results = await self._validate_recovery()
            results["phases"]["recovery_validation"] = recovery_results
            
            # Wait for metrics collection to complete
            await metrics_task
            
            # Generate final report
            results["end_time"] = datetime.now().isoformat()
            results["duration_minutes"] = (datetime.now() - start_time).total_seconds() / 60
            results["metrics_report"] = self.metrics_collector.generate_experiment_report(experiment_id)
            results["status"] = "completed"
            results["overall_success"] = self._calculate_overall_success(results)
            
            logger.info(f"✅ Child Safety Chaos Experiment completed: {results['overall_success']}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Child Safety Chaos Experiment failed: {e}")
            
            # Emergency recovery
            await restore_all_systems()
            
            return {
                "experiment_id": experiment_id,
                "status": "failed",
                "error": str(e),
                "end_time": datetime.now().isoformat()
            }
    
    async def run_resilience_test(self, target_services: List[str], intensity: float = 0.5) -> Dict[str, Any]:
        """Run system resilience test"""
        
        logger.info(f"🏋️ Starting Resilience Test for {target_services}")
        
        experiment_id = f"resilience_{int(time.time())}"
        
        # Define failure types to test
        failure_types = [
            FailureType.NETWORK_LATENCY,
            FailureType.MEMORY_PRESSURE,
            FailureType.SERVICE_CRASH
        ]
        
        try:
            # Run resilience experiment
            metrics = await self.orchestrator.execute_chaos_experiment(
                experiment_name="system_resilience",
                targets=target_services,
                failure_types=failure_types,
                duration_minutes=5,
                intensity=intensity
            )
            
            return {
                "experiment_id": experiment_id,
                "type": "resilience_test",
                "targets": target_services,
                "intensity": intensity,
                "metrics": {
                    "failures_injected": metrics.failures_injected,
                    "failures_detected": metrics.failures_detected,
                    "recovery_time": metrics.recovery_time_seconds,
                    "success_rate": metrics.success_rate,
                    "safety_violations": metrics.safety_violations
                },
                "passed": metrics.success_rate > 0.8 and metrics.safety_violations == 0
            }
            
        except Exception as e:
            logger.error(f"❌ Resilience test failed: {e}")
            return {
                "experiment_id": experiment_id,
                "type": "resilience_test",
                "error": str(e),
                "passed": False
            }
    
    async def run_performance_chaos(self, duration_minutes: int = 10) -> Dict[str, Any]:
        """Run performance-focused chaos test"""
        
        logger.info(f"⚡ Starting Performance Chaos Test ({duration_minutes} minutes)")
        
        experiment_id = f"performance_{int(time.time())}"
        
        try:
            # Start performance monitoring
            metrics_task = asyncio.create_task(
                self.metrics_collector.start_monitoring(experiment_id, duration_minutes * 60)
            )
            
            # Gradually increase load and inject failures
            results = []
            
            for intensity in [0.3, 0.5, 0.7, 0.9]:
                logger.info(f"🔥 Intensity level: {intensity}")
                
                # Run short chaos burst
                burst_metrics = await self.orchestrator.execute_chaos_experiment(
                    experiment_name=f"performance_burst_{intensity}",
                    targets=["ai-service", "graphql-federation"],
                    failure_types=[FailureType.CPU_SPIKE, FailureType.MEMORY_PRESSURE],
                    duration_minutes=2,
                    intensity=intensity
                )
                
                results.append({
                    "intensity": intensity,
                    "success_rate": burst_metrics.success_rate,
                    "recovery_time": burst_metrics.recovery_time_seconds
                })
                
                # Brief recovery period
                await asyncio.sleep(30)
            
            # Wait for monitoring to complete
            await metrics_task
            
            # Calculate performance degradation
            avg_success_rate = sum(r["success_rate"] for r in results) / len(results)
            max_recovery_time = max(r["recovery_time"] for r in results)
            
            return {
                "experiment_id": experiment_id,
                "type": "performance_chaos",
                "duration_minutes": duration_minutes,
                "intensity_tests": results,
                "summary": {
                    "avg_success_rate": avg_success_rate,
                    "max_recovery_time": max_recovery_time,
                    "performance_maintained": avg_success_rate > 0.7
                },
                "metrics_report": self.metrics_collector.generate_experiment_report(experiment_id)
            }
            
        except Exception as e:
            logger.error(f"❌ Performance chaos test failed: {e}")
            return {
                "experiment_id": experiment_id,
                "type": "performance_chaos",
                "error": str(e)
            }
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        
        services = ["child-service", "ai-service", "safety-service", "graphql-federation"]
        health_results = {}
        
        for service in services:
            try:
                import requests
                response = requests.get(f"http://{service}:8000/health", timeout=10)
                health_results[service] = response.status_code == 200
            except:
                health_results[service] = False
        
        all_healthy = all(health_results.values())
        healthy_count = sum(health_results.values())
        
        return {
            "all_healthy": all_healthy,
            "healthy_services": healthy_count,
            "total_services": len(services),
            "health_ratio": healthy_count / len(services),
            "service_health": health_results
        }
    
    async def _run_safety_tests(self) -> Dict[str, Any]:
        """Run safety system tests"""
        
        tests = {}
        
        # Test toxic content injection
        tests["toxic_content"] = await inject_toxic_content()
        
        # Test parental control bypass
        tests["parental_controls"] = await test_parental_controls_bypass()
        
        # Calculate overall safety score
        passed_tests = sum(1 for test in tests.values() if test.get("passed", False))
        safety_score = passed_tests / len(tests)
        
        return {
            "tests": tests,
            "total_tests": len(tests),
            "passed_tests": passed_tests,
            "safety_score": safety_score,
            "all_passed": safety_score == 1.0
        }
    
    async def _run_ai_safety_tests(self) -> Dict[str, Any]:
        """Run AI safety tests"""
        
        tests = {}
        
        # Test hallucination detection
        tests["hallucination_detection"] = await trigger_hallucination()
        
        # Test bias detection
        tests["bias_detection"] = await test_bias_detection()
        
        # Calculate AI safety score
        passed_tests = sum(1 for test in tests.values() if test.get("passed", False))
        ai_safety_score = passed_tests / len(tests)
        
        return {
            "tests": tests,
            "total_tests": len(tests),
            "passed_tests": passed_tests,
            "ai_safety_score": ai_safety_score,
            "all_passed": ai_safety_score == 1.0
        }
    
    async def _inject_controlled_failures(self, experiment_id: str) -> Dict[str, Any]:
        """Inject controlled failures"""
        
        failure_results = {}
        
        try:
            # Network latency injection
            failure_results["network_latency"] = await self.orchestrator.execute_chaos_experiment(
                experiment_name="network_latency_test",
                targets=["child-service", "ai-service"],
                failure_types=[FailureType.NETWORK_LATENCY],
                duration_minutes=3,
                intensity=0.5
            )
            
            await asyncio.sleep(30)  # Recovery time
            
            # Memory pressure injection
            failure_results["memory_pressure"] = await self.orchestrator.execute_chaos_experiment(
                experiment_name="memory_pressure_test",
                targets=["ai-service"],
                failure_types=[FailureType.MEMORY_PRESSURE],
                duration_minutes=2,
                intensity=0.6
            )
            
            await asyncio.sleep(30)  # Recovery time
            
            # Database failure simulation
            failure_results["database_failure"] = await self.orchestrator.execute_chaos_experiment(
                experiment_name="database_failure_test",
                targets=["child-service"],
                failure_types=[FailureType.DATABASE_FAILURE],
                duration_minutes=2,
                intensity=0.4
            )
            
            return {
                "failure_injections": failure_results,
                "total_injections": len(failure_results),
                "successful_injections": sum(1 for r in failure_results.values() if r.success_rate > 0)
            }
            
        except Exception as e:
            logger.error(f"Failure injection error: {e}")
            return {"error": str(e), "successful_injections": 0}
    
    async def _validate_recovery(self) -> Dict[str, Any]:
        """Validate system recovery"""
        
        try:
            # Run recovery validation
            recovery_result = await validate_system_recovery()
            
            # Additional health check
            health_check = await self._check_system_health()
            
            return {
                "recovery_validation": recovery_result,
                "final_health_check": health_check,
                "fully_recovered": (
                    recovery_result.get("overall_success", False) and
                    health_check.get("all_healthy", False)
                )
            }
            
        except Exception as e:
            logger.error(f"Recovery validation error: {e}")
            return {"error": str(e), "fully_recovered": False}
    
    def _calculate_overall_success(self, results: Dict[str, Any]) -> bool:
        """Calculate overall experiment success"""
        
        try:
            phases = results.get("phases", {})
            
            # Check each phase
            baseline_ok = phases.get("baseline_health", {}).get("all_healthy", False)
            safety_ok = phases.get("safety_tests", {}).get("all_passed", False)
            ai_safety_ok = phases.get("ai_safety_tests", {}).get("all_passed", False)
            recovery_ok = phases.get("recovery_validation", {}).get("fully_recovered", False)
            
            # At least 80% success rate required
            success_count = sum([baseline_ok, safety_ok, ai_safety_ok, recovery_ok])
            success_rate = success_count / 4
            
            return success_rate >= 0.75  # 75% success rate threshold
            
        except Exception as e:
            logger.error(f"Error calculating success: {e}")
            return False

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="Chaos Engineering Experiment Runner")
    parser.add_argument("--experiment", choices=["safety", "resilience", "performance"], 
                       default="safety", help="Type of experiment to run")
    parser.add_argument("--targets", nargs="+", 
                       default=["child-service", "ai-service", "safety-service"],
                       help="Target services for experiment")
    parser.add_argument("--intensity", type=float, default=0.5, 
                       help="Experiment intensity (0.0-1.0)")
    parser.add_argument("--duration", type=int, default=10, 
                       help="Experiment duration in minutes")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--output", type=str, help="Output file for results")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)
    
    async def run_experiment():
        runner = ChaosExperimentRunner()
        
        try:
            if args.experiment == "safety":
                results = await runner.run_child_safety_experiment(config)
            elif args.experiment == "resilience":
                results = await runner.run_resilience_test(args.targets, args.intensity)
            elif args.experiment == "performance":
                results = await runner.run_performance_chaos(args.duration)
            else:
                logger.error(f"Unknown experiment type: {args.experiment}")
                return
            
            # Output results
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                logger.info(f"Results saved to {args.output}")
            else:
                print("\n" + "="*80)
                print("CHAOS EXPERIMENT RESULTS")
                print("="*80)
                print(json.dumps(results, indent=2))
            
            # Exit code based on success
            if results.get("overall_success", False) or results.get("passed", False):
                logger.info("✅ Experiment PASSED")
                sys.exit(0)
            else:
                logger.error("❌ Experiment FAILED")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Experiment execution failed: {e}")
            sys.exit(1)
    
    # Print banner
    print("\n" + "="*80)
    print("🧸 AI TEDDY BEAR CHAOS ENGINEERING")
    print("   SRE Team - Task 15")
    print("="*80)
    print(f"Experiment: {args.experiment}")
    print(f"Targets: {args.targets}")
    print(f"Intensity: {args.intensity}")
    print(f"Duration: {args.duration} minutes")
    print("="*80 + "\n")
    
    # Run experiment
    asyncio.run(run_experiment())

if __name__ == "__main__":
    main() 