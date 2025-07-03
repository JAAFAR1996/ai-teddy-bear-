#!/usr/bin/env python3
"""
📋 Contract Testing Framework - AI Teddy Bear Project
اختبارات العقد لضمان توافق APIs والخدمات

Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise Grade AI Teddy Bear Project 2025
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiohttp
import pytest
from pydantic import BaseModel, Field, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractDefinition(BaseModel):
    """تعريف عقد API"""
    name: str
    version: str
    provider: str
    consumer: str
    endpoint: str
    method: str
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    headers: Dict[str, str] = Field(default_factory=dict)
    timeout_seconds: int = 30

class ContractTest(BaseModel):
    """اختبار عقد واحد"""
    name: str
    description: str
    contract: ContractDefinition
    test_data: Dict[str, Any]
    expected_status: int = 200
    expected_response_keys: List[str] = Field(default_factory=list)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)

class ContractResult(BaseModel):
    """نتيجة اختبار عقد"""
    test_name: str
    contract_name: str
    status: str  # passed, failed, error
    request_sent: Dict[str, Any]
    response_received: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    validation_errors: List[str] = Field(default_factory=list)
    execution_time: float = 0.0
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ContractTestSuite(BaseModel):
    """مجموعة اختبارات العقد"""
    name: str
    description: str
    provider: str
    consumer: str
    contracts: List[ContractDefinition] = Field(default_factory=list)
    test_results: List[ContractResult] = Field(default_factory=list)
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    execution_time: float = 0.0

class ContractTestingFramework:
    """إطار اختبارات العقد الشامل"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_suites: Dict[str, ContractTestSuite] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def run_contract_testing(self) -> Dict[str, Any]:
        """تشغيل جميع اختبارات العقد"""
        logger.info("📋 بدء اختبارات العقد...")
        
        start_time = asyncio.get_event_loop().time()
        
        # Define contracts for different services
        await self._test_child_service_contracts()
        await self._test_audio_service_contracts()
        await self._test_ai_service_contracts()
        await self._test_security_service_contracts()
        await self._test_parent_service_contracts()
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        # Calculate overall results
        overall_results = self._calculate_overall_results()
        
        return {
            "test_suites": self.test_suites,
            "overall_results": overall_results,
            "execution_time": execution_time,
            "recommendations": self._generate_recommendations()
        }
    
    async def _test_child_service_contracts(self):
        """اختبار عقود خدمة الطفل"""
        suite = ContractTestSuite(
            name="Child Service Contracts",
            description="عقود API لخدمة الطفل",
            provider="child-service",
            consumer="ai-teddy-bear"
        )
        
        # Contract 1: Get Child Profile
        child_profile_contract = ContractDefinition(
            name="Get Child Profile",
            version="1.0",
            provider="child-service",
            consumer="ai-teddy-bear",
            endpoint="/api/v1/children/{child_id}",
            method="GET",
            request_schema={
                "type": "object",
                "properties": {
                    "child_id": {"type": "string", "format": "uuid"}
                },
                "required": ["child_id"]
            },
            response_schema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "age": {"type": "integer", "minimum": 0, "maximum": 18},
                    "preferences": {"type": "object"},
                    "safety_settings": {"type": "object"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                },
                "required": ["id", "name", "age", "preferences", "safety_settings"]
            }
        )
        
        suite.contracts.append(child_profile_contract)
        
        # Test the contract
        test = ContractTest(
            name="test_get_child_profile_contract",
            description="اختبار عقد الحصول على ملف الطفل",
            contract=child_profile_contract,
            test_data={"child_id": "test-child-123"},
            expected_status=200,
            expected_response_keys=["id", "name", "age", "preferences", "safety_settings"]
        )
        
        result = await self._execute_contract_test(test)
        suite.test_results.append(result)
        suite.total_tests += 1
        
        if result.status == "passed":
            suite.passed_tests += 1
        elif result.status == "failed":
            suite.failed_tests += 1
        else:
            suite.error_tests += 1
        
        self.test_suites["child-service"] = suite
    
    async def _test_audio_service_contracts(self):
        """اختبار عقود خدمة الصوت"""
        suite = ContractTestSuite(
            name="Audio Service Contracts",
            description="عقود API لخدمة معالجة الصوت",
            provider="audio-service",
            consumer="ai-teddy-bear"
        )
        
        # Contract 1: Process Audio
        audio_process_contract = ContractDefinition(
            name="Process Audio",
            version="1.0",
            provider="audio-service",
            consumer="ai-teddy-bear",
            endpoint="/api/v1/audio/process",
            method="POST",
            request_schema={
                "type": "object",
                "properties": {
                    "audio_data": {"type": "string", "format": "base64"},
                    "format": {"type": "string", "enum": ["wav", "mp3", "flac"]},
                    "sample_rate": {"type": "integer", "minimum": 8000, "maximum": 48000},
                    "language": {"type": "string", "default": "en"}
                },
                "required": ["audio_data", "format"]
            },
            response_schema={
                "type": "object",
                "properties": {
                    "transcription": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "language_detected": {"type": "string"},
                    "processing_time_ms": {"type": "number"},
                    "status": {"type": "string", "enum": ["success", "error"]}
                },
                "required": ["transcription", "confidence", "status"]
            }
        )
        
        suite.contracts.append(audio_process_contract)
        
        # Test the contract
        test = ContractTest(
            name="test_audio_process_contract",
            description="اختبار عقد معالجة الصوت",
            contract=audio_process_contract,
            test_data={
                "audio_data": "base64_encoded_audio_data",
                "format": "wav",
                "sample_rate": 16000,
                "language": "en"
            },
            expected_status=200,
            expected_response_keys=["transcription", "confidence", "status"]
        )
        
        result = await self._execute_contract_test(test)
        suite.test_results.append(result)
        suite.total_tests += 1
        
        if result.status == "passed":
            suite.passed_tests += 1
        elif result.status == "failed":
            suite.failed_tests += 1
        else:
            suite.error_tests += 1
        
        self.test_suites["audio-service"] = suite
    
    async def _test_ai_service_contracts(self):
        """اختبار عقود خدمة الذكاء الاصطناعي"""
        suite = ContractTestSuite(
            name="AI Service Contracts",
            description="عقود API لخدمة الذكاء الاصطناعي",
            provider="ai-service",
            consumer="ai-teddy-bear"
        )
        
        # Contract 1: Generate Response
        ai_response_contract = ContractDefinition(
            name="Generate AI Response",
            version="1.0",
            provider="ai-service",
            consumer="ai-teddy-bear",
            endpoint="/api/v1/ai/generate-response",
            method="POST",
            request_schema={
                "type": "object",
                "properties": {
                    "child_id": {"type": "string", "format": "uuid"},
                    "message": {"type": "string"},
                    "context": {"type": "object"},
                    "safety_level": {"type": "string", "enum": ["strict", "moderate", "relaxed"]},
                    "response_type": {"type": "string", "enum": ["text", "audio", "both"]}
                },
                "required": ["child_id", "message"]
            },
            response_schema={
                "type": "object",
                "properties": {
                    "response": {"type": "string"},
                    "audio_url": {"type": "string", "format": "uri"},
                    "safety_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "emotion_detected": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "processing_time_ms": {"type": "number"}
                },
                "required": ["response", "safety_score"]
            }
        )
        
        suite.contracts.append(ai_response_contract)
        
        # Test the contract
        test = ContractTest(
            name="test_ai_response_contract",
            description="اختبار عقد توليد استجابة الذكاء الاصطناعي",
            contract=ai_response_contract,
            test_data={
                "child_id": "test-child-123",
                "message": "Hello Teddy!",
                "context": {"previous_messages": []},
                "safety_level": "strict",
                "response_type": "text"
            },
            expected_status=200,
            expected_response_keys=["response", "safety_score"]
        )
        
        result = await self._execute_contract_test(test)
        suite.test_results.append(result)
        suite.total_tests += 1
        
        if result.status == "passed":
            suite.passed_tests += 1
        elif result.status == "failed":
            suite.failed_tests += 1
        else:
            suite.error_tests += 1
        
        self.test_suites["ai-service"] = suite
    
    async def _test_security_service_contracts(self):
        """اختبار عقود خدمة الأمان"""
        suite = ContractTestSuite(
            name="Security Service Contracts",
            description="عقود API لخدمة الأمان",
            provider="security-service",
            consumer="ai-teddy-bear"
        )
        
        # Contract 1: Validate Token
        token_validation_contract = ContractDefinition(
            name="Validate Security Token",
            version="1.0",
            provider="security-service",
            consumer="ai-teddy-bear",
            endpoint="/api/v1/security/validate-token",
            method="POST",
            request_schema={
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "device_id": {"type": "string"},
                    "permissions": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["token", "device_id"]
            },
            response_schema={
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "user_id": {"type": "string", "format": "uuid"},
                    "permissions": {"type": "array", "items": {"type": "string"}},
                    "expires_at": {"type": "string", "format": "date-time"},
                    "device_verified": {"type": "boolean"}
                },
                "required": ["valid", "user_id", "permissions"]
            }
        )
        
        suite.contracts.append(token_validation_contract)
        
        # Test the contract
        test = ContractTest(
            name="test_token_validation_contract",
            description="اختبار عقد التحقق من الرمز المميز",
            contract=token_validation_contract,
            test_data={
                "token": "test-jwt-token",
                "device_id": "test-device-123",
                "permissions": ["read:child", "write:conversation"]
            },
            expected_status=200,
            expected_response_keys=["valid", "user_id", "permissions"]
        )
        
        result = await self._execute_contract_test(test)
        suite.test_results.append(result)
        suite.total_tests += 1
        
        if result.status == "passed":
            suite.passed_tests += 1
        elif result.status == "failed":
            suite.failed_tests += 1
        else:
            suite.error_tests += 1
        
        self.test_suites["security-service"] = suite
    
    async def _test_parent_service_contracts(self):
        """اختبار عقود خدمة الوالدين"""
        suite = ContractTestSuite(
            name="Parent Service Contracts",
            description="عقود API لخدمة الوالدين",
            provider="parent-service",
            consumer="ai-teddy-bear"
        )
        
        # Contract 1: Get Parent Dashboard
        parent_dashboard_contract = ContractDefinition(
            name="Get Parent Dashboard",
            version="1.0",
            provider="parent-service",
            consumer="ai-teddy-bear",
            endpoint="/api/v1/parents/{parent_id}/dashboard",
            method="GET",
            request_schema={
                "type": "object",
                "properties": {
                    "parent_id": {"type": "string", "format": "uuid"},
                    "date_range": {"type": "string", "enum": ["today", "week", "month", "year"]}
                },
                "required": ["parent_id"]
            },
            response_schema={
                "type": "object",
                "properties": {
                    "parent_id": {"type": "string", "format": "uuid"},
                    "children": {"type": "array", "items": {"type": "object"}},
                    "conversation_summary": {"type": "object"},
                    "safety_alerts": {"type": "array", "items": {"type": "object"}},
                    "learning_progress": {"type": "object"},
                    "last_updated": {"type": "string", "format": "date-time"}
                },
                "required": ["parent_id", "children", "conversation_summary"]
            }
        )
        
        suite.contracts.append(parent_dashboard_contract)
        
        # Test the contract
        test = ContractTest(
            name="test_parent_dashboard_contract",
            description="اختبار عقد لوحة تحكم الوالدين",
            contract=parent_dashboard_contract,
            test_data={
                "parent_id": "test-parent-123",
                "date_range": "week"
            },
            expected_status=200,
            expected_response_keys=["parent_id", "children", "conversation_summary"]
        )
        
        result = await self._execute_contract_test(test)
        suite.test_results.append(result)
        suite.total_tests += 1
        
        if result.status == "passed":
            suite.passed_tests += 1
        elif result.status == "failed":
            suite.failed_tests += 1
        else:
            suite.error_tests += 1
        
        self.test_suites["parent-service"] = suite
    
    async def _execute_contract_test(self, test: ContractTest) -> ContractResult:
        """تنفيذ اختبار عقد واحد"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate request against schema
            self._validate_against_schema(test.test_data, test.contract.request_schema)
            
            # Prepare request
            url = f"{self.base_url}{test.contract.endpoint}"
            if test.contract.method == "GET" and "{child_id}" in url:
                url = url.replace("{child_id}", test.test_data.get("child_id", "test"))
            elif test.contract.method == "GET" and "{parent_id}" in url:
                url = url.replace("{parent_id}", test.test_data.get("parent_id", "test"))
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                **test.contract.headers
            }
            
            # Make request
            if test.contract.method == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.status == 200 else None
                    response_status = response.status
            elif test.contract.method == "POST":
                async with self.session.post(url, json=test.test_data, headers=headers) as response:
                    response_data = await response.json() if response.status == 200 else None
                    response_status = response.status
            else:
                raise ValueError(f"Unsupported method: {test.contract.method}")
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Validate response
            validation_errors = []
            if response_status == test.expected_status and response_data:
                try:
                    self._validate_against_schema(response_data, test.contract.response_schema)
                    
                    # Check required response keys
                    for key in test.expected_response_keys:
                        if key not in response_data:
                            validation_errors.append(f"Missing required key: {key}")
                    
                except ValidationError as e:
                    validation_errors.append(f"Response schema validation failed: {e}")
            
            # Determine test status
            if response_status != test.expected_status:
                status = "failed"
                error_message = f"Expected status {test.expected_status}, got {response_status}"
            elif validation_errors:
                status = "failed"
                error_message = "; ".join(validation_errors)
            else:
                status = "passed"
                error_message = None
            
            return ContractResult(
                test_name=test.name,
                contract_name=test.contract.name,
                status=status,
                request_sent=test.test_data,
                response_received=response_data,
                response_status=response_status,
                validation_errors=validation_errors,
                execution_time=execution_time,
                error_message=error_message
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ContractResult(
                test_name=test.name,
                contract_name=test.contract.name,
                status="error",
                request_sent=test.test_data,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _validate_against_schema(self, data: Any, schema: Dict[str, Any]) -> None:
        """التحقق من صحة البيانات ضد المخطط"""
        # This is a simplified validation - in production, use a proper JSON schema validator
        if not isinstance(data, dict):
            raise ValidationError("Data must be an object")
        
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        properties = schema.get("properties", {})
        for field, value in data.items():
            if field in properties:
                field_schema = properties[field]
                self._validate_field(value, field_schema, field)
    
    def _validate_field(self, value: Any, schema: Dict[str, Any], field_name: str) -> None:
        """التحقق من صحة حقل واحد"""
        field_type = schema.get("type")
        
        if field_type == "string":
            if not isinstance(value, str):
                raise ValidationError(f"Field {field_name} must be a string")
            
            if "enum" in schema and value not in schema["enum"]:
                raise ValidationError(f"Field {field_name} must be one of {schema['enum']}")
                
        elif field_type == "integer":
            if not isinstance(value, int):
                raise ValidationError(f"Field {field_name} must be an integer")
            
            if "minimum" in schema and value < schema["minimum"]:
                raise ValidationError(f"Field {field_name} must be >= {schema['minimum']}")
            
            if "maximum" in schema and value > schema["maximum"]:
                raise ValidationError(f"Field {field_name} must be <= {schema['maximum']}")
                
        elif field_type == "number":
            if not isinstance(value, (int, float)):
                raise ValidationError(f"Field {field_name} must be a number")
                
        elif field_type == "boolean":
            if not isinstance(value, bool):
                raise ValidationError(f"Field {field_name} must be a boolean")
                
        elif field_type == "array":
            if not isinstance(value, list):
                raise ValidationError(f"Field {field_name} must be an array")
                
        elif field_type == "object":
            if not isinstance(value, dict):
                raise ValidationError(f"Field {field_name} must be an object")
    
    def _calculate_overall_results(self) -> Dict[str, Any]:
        """حساب النتائج الإجمالية"""
        total_tests = sum(suite.total_tests for suite in self.test_suites.values())
        passed_tests = sum(suite.passed_tests for suite in self.test_suites.values())
        failed_tests = sum(suite.failed_tests for suite in self.test_suites.values())
        error_tests = sum(suite.error_tests for suite in self.test_suites.values())
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": success_rate,
            "services_tested": len(self.test_suites)
        }
    
    def _generate_recommendations(self) -> List[str]:
        """توليد توصيات لتحسين العقود"""
        recommendations = []
        
        overall_results = self._calculate_overall_results()
        
        if overall_results["success_rate"] < 90:
            recommendations.append("🔴 معدل نجاح العقود منخفض - راجع تعريفات APIs")
        
        if overall_results["error_tests"] > 0:
            recommendations.append("🟡 بعض الاختبارات فشلت - تحقق من توفر الخدمات")
        
        for service_name, suite in self.test_suites.items():
            if suite.failed_tests > 0:
                recommendations.append(f"🔴 {service_name}: {suite.failed_tests} اختبارات فشلت")
        
        if not recommendations:
            recommendations.append("✅ جميع العقود تعمل بشكل صحيح")
        
        return recommendations

# Test the contract testing framework
async def test_contract_framework():
    """اختبار إطار اختبارات العقد"""
    async with ContractTestingFramework() as framework:
        results = await framework.run_contract_testing()
        
        print("📋 نتائج اختبارات العقد:")
        print(f"إجمالي الاختبارات: {results['overall_results']['total_tests']}")
        print(f"الاختبارات الناجحة: {results['overall_results']['passed_tests']}")
        print(f"معدل النجاح: {results['overall_results']['success_rate']:.1f}%")
        
        print("\n📋 التوصيات:")
        for rec in results['recommendations']:
            print(f"  {rec}")

if __name__ == "__main__":
    asyncio.run(test_contract_framework()) 