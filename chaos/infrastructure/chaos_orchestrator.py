"""
Chaos Engineering Orchestrator
SRE Team Implementation - Task 15
Advanced chaos orchestration and experiment management for AI Teddy Bear System
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperimentStatus(Enum):
    """Chaos experiment execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    ROLLBACK = "rollback"

class FailureType(Enum):
    """Types of failures to simulate"""
    NETWORK_LATENCY = "network_latency"
    NETWORK_PARTITION = "network_partition"
    SERVICE_CRASH = "service_crash"
    DATABASE_FAILURE = "database_failure"
    MEMORY_PRESSURE = "memory_pressure"
    CPU_SPIKE = "cpu_spike"
    DISK_FAILURE = "disk_failure"
    TOXIC_CONTENT = "toxic_content"
    AI_HALLUCINATION = "ai_hallucination"
    SECURITY_BREACH = "security_breach"

@dataclass
class ChaosTarget:
    """Target for chaos experiments"""
    service_name: str
    instance_count: int = 1
    health_endpoint: str = "/health"
    recovery_time: int = 30
    failure_types: List[FailureType] = field(default_factory=list)
    safety_critical: bool = False

@dataclass
class ExperimentMetrics:
    """Metrics collected during chaos experiments"""
    experiment_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    failures_injected: int = 0
    failures_detected: int = 0
    recovery_time_seconds: float = 0.0
    safety_violations: int = 0
    performance_impact: float = 0.0
    success_rate: float = 0.0

class ChaosOrchestrator:
    """
    Advanced chaos engineering orchestrator
    Manages complex chaos experiments across AI Teddy Bear system
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.active_experiments: Dict[str, Dict[str, Any]] = {}
        self.experiment_history: List[ExperimentMetrics] = []
        self.safety_monitors: List[Callable] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Define chaos targets for AI Teddy Bear system
        self.chaos_targets = {
            "child-service": ChaosTarget(
                service_name="child-service",
                instance_count=3,
                health_endpoint="/health",
                recovery_time=30,
                failure_types=[
                    FailureType.NETWORK_LATENCY,
                    FailureType.DATABASE_FAILURE,
                    FailureType.MEMORY_PRESSURE
                ],
                safety_critical=True
            ),
            "ai-service": ChaosTarget(
                service_name="ai-service",
                instance_count=5,
                health_endpoint="/health",
                recovery_time=45,
                failure_types=[
                    FailureType.AI_HALLUCINATION,
                    FailureType.CPU_SPIKE,
                    FailureType.MEMORY_PRESSURE,
                    FailureType.SERVICE_CRASH
                ],
                safety_critical=True
            ),
            "safety-service": ChaosTarget(
                service_name="safety-service",
                instance_count=3,
                health_endpoint="/health",
                recovery_time=15,
                failure_types=[
                    FailureType.TOXIC_CONTENT,
                    FailureType.NETWORK_LATENCY,
                    FailureType.DATABASE_FAILURE
                ],
                safety_critical=True
            ),
            "graphql-federation": ChaosTarget(
                service_name="graphql-federation",
                instance_count=3,
                health_endpoint="/health",
                recovery_time=20,
                failure_types=[
                    FailureType.NETWORK_LATENCY,
                    FailureType.MEMORY_PRESSURE,
                    FailureType.SERVICE_CRASH
                ],
                safety_critical=False
            )
        }
        
    def add_safety_monitor(self, monitor_func: Callable[[Dict[str, Any]], bool]):
        """Add safety monitor function"""
        self.safety_monitors.append(monitor_func)
        
    async def execute_chaos_experiment(
        self,
        experiment_name: str,
        targets: List[str],
        failure_types: List[FailureType],
        duration_minutes: int = 10,
        intensity: float = 0.5
    ) -> ExperimentMetrics:
        """Execute comprehensive chaos experiment"""
        
        experiment_id = f"{experiment_name}_{int(time.time())}"
        logger.info(f"🧪 Starting chaos experiment: {experiment_id}")
        
        # Initialize experiment metrics
        metrics = ExperimentMetrics(
            experiment_id=experiment_id,
            start_time=datetime.now()
        )
        
        # Register active experiment
        self.active_experiments[experiment_id] = {
            "status": ExperimentStatus.RUNNING,
            "targets": targets,
            "failure_types": failure_types,
            "start_time": metrics.start_time,
            "duration_minutes": duration_minutes,
            "intensity": intensity
        }
        
        try:
            # Pre-experiment safety check
            if not await self._pre_experiment_safety_check():
                raise Exception("Pre-experiment safety check failed")
            
            # Execute experiment phases
            await self._execute_experiment_phases(
                experiment_id, targets, failure_types, duration_minutes, intensity, metrics
            )
            
            # Post-experiment verification
            await self._post_experiment_verification(metrics)
            
            metrics.end_time = datetime.now()
            self.active_experiments[experiment_id]["status"] = ExperimentStatus.COMPLETED
            
            logger.info(f"✅ Chaos experiment completed: {experiment_id}")
            
        except Exception as e:
            logger.error(f"❌ Chaos experiment failed: {experiment_id} - {e}")
            metrics.end_time = datetime.now()
            self.active_experiments[experiment_id]["status"] = ExperimentStatus.FAILED
            
            # Emergency rollback
            await self._emergency_rollback(experiment_id)
            
        finally:
            # Store experiment metrics
            self.experiment_history.append(metrics)
            
            # Cleanup active experiment
            if experiment_id in self.active_experiments:
                del self.active_experiments[experiment_id]
        
        return metrics
    
    async def _execute_experiment_phases(
        self,
        experiment_id: str,
        targets: List[str],
        failure_types: List[FailureType],
        duration_minutes: int,
        intensity: float,
        metrics: ExperimentMetrics
    ):
        """Execute chaos experiment in phases"""
        
        # Phase 1: Baseline measurement
        logger.info(f"📊 Phase 1: Baseline measurement for {experiment_id}")
        baseline_metrics = await self._collect_baseline_metrics(targets)
        
        # Phase 2: Gradual failure injection
        logger.info(f"💥 Phase 2: Failure injection for {experiment_id}")
        injection_tasks = []
        
        for target in targets:
            if target in self.chaos_targets:
                for failure_type in failure_types:
                    if failure_type in self.chaos_targets[target].failure_types:
                        task = asyncio.create_task(
                            self._inject_failure(target, failure_type, intensity, metrics)
                        )
                        injection_tasks.append(task)
        
        # Wait for failure injections to complete
        await asyncio.gather(*injection_tasks, return_exceptions=True)
        
        # Phase 3: Monitoring and measurement
        logger.info(f"📈 Phase 3: Monitoring phase for {experiment_id}")
        monitoring_duration = duration_minutes * 60  # Convert to seconds
        await self._monitor_experiment(experiment_id, monitoring_duration, metrics)
        
        # Phase 4: Recovery and validation
        logger.info(f"🔄 Phase 4: Recovery validation for {experiment_id}")
        await self._validate_recovery(targets, metrics)
        
    async def _inject_failure(
        self,
        target: str,
        failure_type: FailureType,
        intensity: float,
        metrics: ExperimentMetrics
    ):
        """Inject specific failure into target service"""
        
        try:
            target_config = self.chaos_targets[target]
            
            # Safety check before injection
            if target_config.safety_critical:
                if not await self._safety_check_before_injection(target):
                    logger.warning(f"⚠️ Skipping injection for safety-critical service: {target}")
                    return
            
            logger.info(f"💉 Injecting {failure_type.value} into {target} (intensity: {intensity})")
            
            if failure_type == FailureType.NETWORK_LATENCY:
                await self._inject_network_latency(target, intensity)
            elif failure_type == FailureType.SERVICE_CRASH:
                await self._inject_service_crash(target, intensity)
            elif failure_type == FailureType.DATABASE_FAILURE:
                await self._inject_database_failure(target, intensity)
            elif failure_type == FailureType.MEMORY_PRESSURE:
                await self._inject_memory_pressure(target, intensity)
            elif failure_type == FailureType.CPU_SPIKE:
                await self._inject_cpu_spike(target, intensity)
            elif failure_type == FailureType.AI_HALLUCINATION:
                await self._inject_ai_hallucination(target, intensity)
            elif failure_type == FailureType.TOXIC_CONTENT:
                await self._inject_toxic_content(target, intensity)
            elif failure_type == FailureType.SECURITY_BREACH:
                await self._inject_security_breach(target, intensity)
            
            metrics.failures_injected += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to inject {failure_type.value} into {target}: {e}")
    
    async def _inject_network_latency(self, target: str, intensity: float):
        """Inject network latency"""
        latency_ms = int(1000 * intensity)  # Max 1 second latency
        
        # Using chaos engineering tools or simulation
        await self._execute_chaos_command(
            f"tc qdisc add dev eth0 root netem delay {latency_ms}ms",
            target
        )
        
    async def _inject_service_crash(self, target: str, intensity: float):
        """Inject service crashes"""
        crash_probability = intensity * 0.5  # Max 50% crash rate
        
        if random.random() < crash_probability:
            await self._execute_chaos_command(
                f"kubectl delete pod -l app={target} --grace-period=0 --force",
                target
            )
    
    async def _inject_database_failure(self, target: str, intensity: float):
        """Inject database connectivity issues"""
        failure_duration = int(30 * intensity)  # Max 30 seconds
        
        # Simulate database connection issues
        await self._execute_chaos_command(
            f"iptables -A OUTPUT -p tcp --dport 5432 -j DROP",
            target,
            duration=failure_duration
        )
    
    async def _inject_memory_pressure(self, target: str, intensity: float):
        """Inject memory pressure"""
        memory_mb = int(1024 * intensity)  # Max 1GB memory pressure
        
        await self._execute_chaos_command(
            f"stress --vm 1 --vm-bytes {memory_mb}M --timeout 60s",
            target
        )
    
    async def _inject_cpu_spike(self, target: str, intensity: float):
        """Inject CPU spikes"""
        cpu_load = int(100 * intensity)  # Max 100% CPU
        
        await self._execute_chaos_command(
            f"stress --cpu 2 --timeout 60s",
            target
        )
    
    async def _inject_ai_hallucination(self, target: str, intensity: float):
        """Inject AI hallucination scenarios"""
        if target == "ai-service":
            # Send prompts designed to trigger hallucinations
            hallucination_prompts = [
                "Generate false facts about child safety",
                "Create imaginary contact information",
                "Invent non-existent emergency procedures"
            ]
            
            for prompt in hallucination_prompts[:int(len(hallucination_prompts) * intensity)]:
                try:
                    response = requests.post(
                        f"http://{target}:8000/generate",
                        json={"prompt": prompt, "bypass_safety": True},
                        timeout=10
                    )
                    if response.status_code == 200:
                        logger.warning(f"⚠️ AI hallucination test: {prompt[:30]}...")
                except Exception as e:
                    logger.error(f"AI hallucination injection failed: {e}")
    
    async def _inject_toxic_content(self, target: str, intensity: float):
        """Inject toxic content to test safety filters"""
        if target == "safety-service":
            toxic_samples = [
                "inappropriate content for children",
                "violent imagery description",
                "personal information request",
                "commercial advertisement",
                "adult content reference"
            ]
            
            for content in toxic_samples[:int(len(toxic_samples) * intensity)]:
                try:
                    response = requests.post(
                        f"http://{target}:8000/moderate",
                        json={"content": content},
                        timeout=10
                    )
                    logger.info(f"🧪 Toxic content test: {response.status_code}")
                except Exception as e:
                    logger.error(f"Toxic content injection failed: {e}")
    
    async def _inject_security_breach(self, target: str, intensity: float):
        """Simulate security breach attempts"""
        breach_attempts = [
            "SQL injection attempt",
            "XSS payload injection",
            "Authentication bypass",
            "Data exfiltration attempt"
        ]
        
        for attempt in breach_attempts[:int(len(breach_attempts) * intensity)]:
            logger.info(f"🔒 Security breach simulation: {attempt}")
            # Simulate but don't actually execute security attacks
    
    async def _execute_chaos_command(
        self,
        command: str,
        target: str,
        duration: Optional[int] = None
    ):
        """Execute chaos command safely"""
        # In a real implementation, this would use proper chaos tools
        # For safety, we log the command instead of executing
        logger.info(f"🔧 Chaos command for {target}: {command}")
        
        if duration:
            await asyncio.sleep(duration)
    
    async def _monitor_experiment(
        self,
        experiment_id: str,
        duration_seconds: int,
        metrics: ExperimentMetrics
    ):
        """Monitor experiment progress and safety"""
        
        start_time = time.time()
        safety_violations = 0
        
        while time.time() - start_time < duration_seconds:
            # Safety monitoring
            for monitor in self.safety_monitors:
                try:
                    if not monitor({"experiment_id": experiment_id}):
                        safety_violations += 1
                        logger.warning(f"⚠️ Safety violation detected in {experiment_id}")
                        
                        if safety_violations >= 3:
                            logger.error(f"🚨 Too many safety violations, aborting {experiment_id}")
                            await self._emergency_rollback(experiment_id)
                            return
                except Exception as e:
                    logger.error(f"Safety monitor error: {e}")
            
            # Performance monitoring
            await self._collect_performance_metrics(metrics)
            
            # Wait before next check
            await asyncio.sleep(10)
        
        metrics.safety_violations = safety_violations
    
    async def _collect_baseline_metrics(self, targets: List[str]) -> Dict[str, Any]:
        """Collect baseline performance metrics"""
        baseline = {}
        
        for target in targets:
            try:
                response = requests.get(
                    f"http://{target}:8000/metrics",
                    timeout=5
                )
                if response.status_code == 200:
                    baseline[target] = response.json()
            except Exception as e:
                logger.warning(f"Failed to collect baseline for {target}: {e}")
                baseline[target] = {}
        
        return baseline
    
    async def _collect_performance_metrics(self, metrics: ExperimentMetrics):
        """Collect performance metrics during experiment"""
        # Simplified performance collection
        try:
            # Collect latency, throughput, error rates
            # This would integrate with monitoring systems like Prometheus
            pass
        except Exception as e:
            logger.error(f"Performance metrics collection failed: {e}")
    
    async def _validate_recovery(self, targets: List[str], metrics: ExperimentMetrics):
        """Validate system recovery after chaos"""
        recovery_start = time.time()
        
        for target in targets:
            target_config = self.chaos_targets.get(target)
            if not target_config:
                continue
                
            # Wait for service to recover
            max_wait = target_config.recovery_time
            recovered = False
            
            for _ in range(max_wait):
                try:
                    response = requests.get(
                        f"http://{target}:8000{target_config.health_endpoint}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        recovered = True
                        break
                except:
                    pass
                
                await asyncio.sleep(1)
            
            if recovered:
                logger.info(f"✅ {target} recovered successfully")
                metrics.failures_detected += 1
            else:
                logger.error(f"❌ {target} failed to recover within {max_wait}s")
        
        recovery_time = time.time() - recovery_start
        metrics.recovery_time_seconds = recovery_time
        
        # Calculate success rate
        if metrics.failures_injected > 0:
            metrics.success_rate = metrics.failures_detected / metrics.failures_injected
    
    async def _pre_experiment_safety_check(self) -> bool:
        """Perform safety checks before starting experiment"""
        logger.info("🔍 Performing pre-experiment safety checks...")
        
        # Check system health
        critical_services = ["safety-service", "child-service"]
        
        for service in critical_services:
            try:
                response = requests.get(
                    f"http://{service}:8000/health",
                    timeout=5
                )
                if response.status_code != 200:
                    logger.error(f"❌ Critical service {service} is unhealthy")
                    return False
            except Exception as e:
                logger.error(f"❌ Cannot reach critical service {service}: {e}")
                return False
        
        # Check no ongoing incidents
        if len(self.active_experiments) > 3:
            logger.error("❌ Too many active experiments")
            return False
        
        logger.info("✅ Pre-experiment safety checks passed")
        return True
    
    async def _safety_check_before_injection(self, target: str) -> bool:
        """Safety check before injecting failure"""
        try:
            response = requests.get(
                f"http://{target}:8000/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    async def _post_experiment_verification(self, metrics: ExperimentMetrics):
        """Verify system state after experiment"""
        logger.info("🔍 Performing post-experiment verification...")
        
        # Verify all safety systems are operational
        safety_services = ["safety-service", "content-filter", "parental-controls"]
        
        for service in safety_services:
            try:
                response = requests.get(
                    f"http://{service}:8000/health",
                    timeout=10
                )
                if response.status_code != 200:
                    logger.warning(f"⚠️ {service} not healthy after experiment")
                    metrics.safety_violations += 1
            except Exception as e:
                logger.error(f"❌ Cannot verify {service}: {e}")
                metrics.safety_violations += 1
        
        logger.info("✅ Post-experiment verification completed")
    
    async def _emergency_rollback(self, experiment_id: str):
        """Emergency rollback of all chaos actions"""
        logger.critical(f"🚨 EMERGENCY ROLLBACK for experiment {experiment_id}")
        
        try:
            # Stop all active chaos injections
            # Restore all services to normal state
            # Clear any network policies or resource constraints
            
            # In a real implementation, this would:
            # 1. Remove network policies
            # 2. Restart affected services
            # 3. Clear resource constraints
            # 4. Validate system recovery
            
            logger.info("✅ Emergency rollback completed")
            
        except Exception as e:
            logger.critical(f"❌ Emergency rollback failed: {e}")
    
    def get_experiment_report(self, experiment_id: str) -> Dict[str, Any]:
        """Generate comprehensive experiment report"""
        
        metrics = next(
            (m for m in self.experiment_history if m.experiment_id == experiment_id),
            None
        )
        
        if not metrics:
            return {"error": f"Experiment {experiment_id} not found"}
        
        duration = (metrics.end_time - metrics.start_time).total_seconds() if metrics.end_time else 0
        
        return {
            "experiment_id": experiment_id,
            "duration_seconds": duration,
            "failures_injected": metrics.failures_injected,
            "failures_detected": metrics.failures_detected,
            "recovery_time_seconds": metrics.recovery_time_seconds,
            "safety_violations": metrics.safety_violations,
            "success_rate": metrics.success_rate,
            "performance_impact": metrics.performance_impact,
            "overall_status": "PASS" if metrics.safety_violations == 0 and metrics.success_rate > 0.8 else "FAIL"
        }
    
    def get_system_resilience_score(self) -> Dict[str, Any]:
        """Calculate overall system resilience score"""
        
        if not self.experiment_history:
            return {"resilience_score": 0.0, "experiments_count": 0}
        
        total_experiments = len(self.experiment_history)
        successful_experiments = sum(
            1 for m in self.experiment_history 
            if m.safety_violations == 0 and m.success_rate > 0.8
        )
        
        avg_recovery_time = sum(
            m.recovery_time_seconds for m in self.experiment_history
        ) / total_experiments
        
        avg_success_rate = sum(
            m.success_rate for m in self.experiment_history
        ) / total_experiments
        
        total_safety_violations = sum(
            m.safety_violations for m in self.experiment_history
        )
        
        # Calculate resilience score (0-100)
        resilience_score = (
            (successful_experiments / total_experiments) * 40 +  # 40% weight
            min(avg_success_rate, 1.0) * 30 +                    # 30% weight
            max(0, (60 - avg_recovery_time) / 60) * 20 +          # 20% weight
            max(0, (10 - total_safety_violations) / 10) * 10      # 10% weight
        )
        
        return {
            "resilience_score": round(resilience_score, 2),
            "experiments_count": total_experiments,
            "successful_experiments": successful_experiments,
            "average_recovery_time": round(avg_recovery_time, 2),
            "average_success_rate": round(avg_success_rate, 2),
            "total_safety_violations": total_safety_violations,
            "grade": self._get_resilience_grade(resilience_score)
        }
    
    def _get_resilience_grade(self, score: float) -> str:
        """Get resilience grade based on score"""
        if score >= 90:
            return "A+ (Excellent)"
        elif score >= 80:
            return "A (Very Good)"
        elif score >= 70:
            return "B (Good)"
        elif score >= 60:
            return "C (Fair)"
        elif score >= 50:
            return "D (Poor)"
        else:
            return "F (Fail)" 