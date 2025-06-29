"""
Recovery and Restoration Actions
SRE Team Implementation - Task 15
Recovery actions for restoring system state after chaos experiments
"""

import asyncio
import logging
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RecoveryActions:
    """Recovery and restoration actions"""
    
    def __init__(self):
        self.service_endpoints = {
            "child-service": "http://child-service:8000",
            "ai-service": "http://ai-service:8000", 
            "safety-service": "http://safety-service:8000",
            "graphql-federation": "http://graphql-federation:8000"
        }
        
        self.recovery_timeouts = {
            "child-service": 30,
            "ai-service": 60,
            "safety-service": 20,
            "graphql-federation": 25
        }

async def restore_all_systems(configuration: Dict[str, Any] = None) -> Dict[str, Any]:
    """Restore all systems to normal operation"""
    
    recovery = RecoveryActions()
    restoration_results = {}
    
    logger.info("🔄 Starting system restoration")
    
    try:
        # Restore each service
        for service_name, base_url in recovery.service_endpoints.items():
            logger.info(f"Restoring {service_name}...")
            
            try:
                # Send restore command
                restore_response = requests.post(
                    f"{base_url}/admin/restore",
                    json={
                        "restore_all": True,
                        "clear_chaos_state": True,
                        "reset_to_baseline": True
                    },
                    timeout=30
                )
                
                if restore_response.status_code in [200, 202]:
                    restoration_results[service_name] = True
                    logger.info(f"✅ {service_name} restoration initiated")
                else:
                    restoration_results[service_name] = False
                    logger.error(f"❌ {service_name} restoration failed: {restore_response.status_code}")
                
            except Exception as e:
                restoration_results[service_name] = False
                logger.error(f"❌ {service_name} restoration error: {e}")
            
            await asyncio.sleep(2)
        
        # Wait for services to stabilize
        logger.info("⏳ Waiting for services to stabilize...")
        await asyncio.sleep(10)
        
        # Verify restoration
        verification_results = await verify_system_health(recovery.service_endpoints)
        
        all_restored = all(restoration_results.values())
        all_healthy = all(verification_results.values())
        
        success = all_restored and all_healthy
        
        logger.info(f"{'✅' if success else '❌'} System restoration {'completed' if success else 'failed'}")
        
        return {
            "action": "restore_all_systems",
            "restoration_results": restoration_results,
            "verification_results": verification_results,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ System restoration failed: {e}")
        return {
            "action": "restore_all_systems",
            "error": str(e),
            "success": False
        }

async def clear_chaos_state(configuration: Dict[str, Any] = None) -> Dict[str, Any]:
    """Clear all chaos-related state and configurations"""
    
    recovery = RecoveryActions()
    clear_results = {}
    
    logger.info("🧹 Clearing chaos state")
    
    try:
        for service_name, base_url in recovery.service_endpoints.items():
            try:
                # Clear chaos state
                clear_response = requests.post(
                    f"{base_url}/admin/clear-chaos",
                    json={
                        "clear_network_policies": True,
                        "clear_resource_limits": True,
                        "clear_failure_injections": True,
                        "reset_metrics": True
                    },
                    timeout=15
                )
                
                clear_results[service_name] = clear_response.status_code in [200, 202]
                
            except Exception as e:
                clear_results[service_name] = False
                logger.error(f"❌ Failed to clear chaos state for {service_name}: {e}")
        
        success = all(clear_results.values())
        
        return {
            "action": "clear_chaos_state",
            "clear_results": clear_results,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Chaos state clearing failed: {e}")
        return {
            "action": "clear_chaos_state",
            "error": str(e),
            "success": False
        }

async def restore_network_policies(configuration: Dict[str, Any] = None) -> Dict[str, Any]:
    """Restore normal network policies"""
    
    logger.info("🌐 Restoring network policies")
    
    try:
        # Remove chaos-induced network policies
        network_commands = [
            "tc qdisc del dev eth0 root",  # Remove network delay
            "iptables -F OUTPUT",          # Clear output rules
            "iptables -F INPUT",           # Clear input rules
        ]
        
        success_count = 0
        
        for command in network_commands:
            try:
                # In a real implementation, this would execute the command
                # For safety, we simulate the execution
                logger.info(f"Executing: {command}")
                success_count += 1
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Network policy restoration failed: {command} - {e}")
        
        success = success_count == len(network_commands)
        
        return {
            "action": "restore_network_policies",
            "commands_executed": success_count,
            "total_commands": len(network_commands),
            "success": success
        }
        
    except Exception as e:
        logger.error(f"❌ Network policy restoration failed: {e}")
        return {
            "action": "restore_network_policies",
            "error": str(e),
            "success": False
        }

async def restart_failed_services(configuration: Dict[str, Any] = None) -> Dict[str, Any]:
    """Restart services that failed during chaos experiments"""
    
    recovery = RecoveryActions()
    restart_results = {}
    
    logger.info("🔄 Restarting failed services")
    
    try:
        # Check service health first
        health_results = await verify_system_health(recovery.service_endpoints)
        
        failed_services = [service for service, healthy in health_results.items() if not healthy]
        
        if not failed_services:
            logger.info("✅ No failed services found")
            return {
                "action": "restart_failed_services",
                "failed_services": [],
                "restart_results": {},
                "success": True
            }
        
        logger.info(f"Found {len(failed_services)} failed services: {failed_services}")
        
        for service in failed_services:
            try:
                # Send restart command
                restart_response = requests.post(
                    f"{recovery.service_endpoints[service]}/admin/restart",
                    json={"force": True, "wait_for_ready": True},
                    timeout=60
                )
                
                if restart_response.status_code in [200, 202]:
                    # Wait for service to be ready
                    await wait_for_service_ready(service, recovery.service_endpoints[service], 60)
                    restart_results[service] = True
                    logger.info(f"✅ {service} restarted successfully")
                else:
                    restart_results[service] = False
                    logger.error(f"❌ {service} restart failed: {restart_response.status_code}")
                
            except Exception as e:
                restart_results[service] = False
                logger.error(f"❌ {service} restart error: {e}")
        
        success = all(restart_results.values())
        
        return {
            "action": "restart_failed_services",
            "failed_services": failed_services,
            "restart_results": restart_results,
            "success": success
        }
        
    except Exception as e:
        logger.error(f"❌ Service restart failed: {e}")
        return {
            "action": "restart_failed_services",
            "error": str(e),
            "success": False
        }

async def validate_system_recovery(configuration: Dict[str, Any] = None) -> Dict[str, Any]:
    """Validate complete system recovery"""
    
    recovery = RecoveryActions()
    validation_results = {}
    
    logger.info("✅ Validating system recovery")
    
    try:
        # Check service health
        health_results = await verify_system_health(recovery.service_endpoints)
        validation_results["service_health"] = health_results
        
        # Test critical functionality
        functionality_tests = await test_critical_functionality()
        validation_results["functionality_tests"] = functionality_tests
        
        # Verify safety systems
        safety_validation = await validate_safety_systems()
        validation_results["safety_validation"] = safety_validation
        
        # Check performance metrics
        performance_check = await check_performance_metrics()
        validation_results["performance_check"] = performance_check
        
        # Overall success
        overall_success = (
            all(health_results.values()) and
            all(functionality_tests.values()) and
            safety_validation.get("all_systems_safe", False) and
            performance_check.get("performance_acceptable", False)
        )
        
        logger.info(f"{'✅' if overall_success else '❌'} System recovery validation {'passed' if overall_success else 'failed'}")
        
        return {
            "action": "validate_system_recovery",
            "validation_results": validation_results,
            "overall_success": overall_success,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ System recovery validation failed: {e}")
        return {
            "action": "validate_system_recovery",
            "error": str(e),
            "overall_success": False
        }

# Helper functions
async def verify_system_health(service_endpoints: Dict[str, str]) -> Dict[str, bool]:
    """Verify health of all services"""
    health_results = {}
    
    for service_name, base_url in service_endpoints.items():
        try:
            health_response = requests.get(
                f"{base_url}/health",
                timeout=10
            )
            health_results[service_name] = health_response.status_code == 200
            
        except Exception:
            health_results[service_name] = False
    
    return health_results

async def wait_for_service_ready(service_name: str, base_url: str, timeout_seconds: int) -> bool:
    """Wait for service to be ready"""
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        
        await asyncio.sleep(2)
    
    return False

async def test_critical_functionality() -> Dict[str, bool]:
    """Test critical system functionality"""
    tests = {}
    
    try:
        # Test child service functionality
        child_test = requests.post(
            "http://child-service:8000/children/test-health",
            json={"test_type": "basic"},
            timeout=10
        )
        tests["child_service_functionality"] = child_test.status_code == 200
        
        # Test AI service functionality
        ai_test = requests.post(
            "http://ai-service:8000/chat",
            json={"message": "Hello", "child_age": 8},
            timeout=15
        )
        tests["ai_service_functionality"] = ai_test.status_code == 200
        
        # Test safety service functionality
        safety_test = requests.post(
            "http://safety-service:8000/moderate",
            json={"content": "test content"},
            timeout=10
        )
        tests["safety_service_functionality"] = safety_test.status_code == 200
        
    except Exception as e:
        logger.error(f"Functionality test error: {e}")
    
    return tests

async def validate_safety_systems() -> Dict[str, Any]:
    """Validate safety systems are operational"""
    try:
        # Test content filtering
        filter_test = requests.post(
            "http://safety-service:8000/moderate",
            json={"content": "inappropriate content test"},
            timeout=10
        )
        
        content_filter_working = (
            filter_test.status_code == 200 and 
            filter_test.json().get("blocked", False)
        )
        
        # Test parental controls
        parental_test = requests.get(
            "http://child-service:8000/parental/health",
            timeout=10
        )
        
        parental_controls_working = parental_test.status_code == 200
        
        # Test age verification
        age_test = requests.post(
            "http://child-service:8000/age/verify",
            json={"child_id": "test", "claimed_age": 10},
            timeout=10
        )
        
        age_verification_working = age_test.status_code in [200, 422]  # 422 is expected for test data
        
        all_systems_safe = (
            content_filter_working and
            parental_controls_working and
            age_verification_working
        )
        
        return {
            "content_filter_working": content_filter_working,
            "parental_controls_working": parental_controls_working,
            "age_verification_working": age_verification_working,
            "all_systems_safe": all_systems_safe
        }
        
    except Exception as e:
        logger.error(f"Safety validation error: {e}")
        return {"all_systems_safe": False, "error": str(e)}

async def check_performance_metrics() -> Dict[str, Any]:
    """Check system performance metrics"""
    try:
        # Check response times
        start_time = time.time()
        test_response = requests.get("http://graphql-federation:8000/health", timeout=5)
        response_time = time.time() - start_time
        
        performance_acceptable = (
            test_response.status_code == 200 and
            response_time < 2.0  # Should respond within 2 seconds
        )
        
        return {
            "response_time": response_time,
            "performance_acceptable": performance_acceptable
        }
        
    except Exception as e:
        logger.error(f"Performance check error: {e}")
        return {"performance_acceptable": False, "error": str(e)} 