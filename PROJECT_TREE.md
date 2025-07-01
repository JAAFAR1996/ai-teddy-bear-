# 🌳 شجرة مشروع AI Teddy Bear

```
AI-Teddy-Bear-Project/
├── .github/
│   └── workflows/
│       ├── code-quality.yml
│       ├── comprehensive-pipeline.yml
│       ├── quality-assurance.yml
│       └── secrets-detection.yml
├── api/
│   ├── endpoints/
│   │   ├── __init__.py
│   │   ├── audio.py
│   │   ├── dashboard.py
│   │   └── device.py
│   └── websocket/
│       └── __init__.py
├── argocd/
│   ├── applications/
│   │   ├── ai-teddy-app.yaml
│   │   └── microservices/
│   │       └── child-service-app.yaml
│   ├── environment-configs/
│   │   └── production.yaml
│   └── workflows/
│       └── ci-cd-integration.yaml
├── chaos/
│   ├── actions/
│   │   ├── ai.py
│   │   ├── recovery.py
│   │   └── safety.py
│   ├── infrastructure/
│   │   └── chaos_orchestrator.py
│   └── monitoring/
│       └── chaos_metrics.py
├── config/
│   ├── environments/
│   │   ├── development.json
│   │   ├── production_config.json
│   │   └── staging_config.json
│   ├── schemas/
│   │   ├── application.json
│   │   ├── audio_processing.json
│   │   ├── common_definitions.json
│   │   └── [+16 more schemas]
│   ├── api_keys.json.example
│   ├── config.json
│   └── default_schema_backup.json
├── configs/
│   ├── __init__.py
│   ├── audio_config.py
│   ├── config_hardware_esp32_analyzer.py
│   └── [+13 more config files]
├── deployments/
│   └── k8s/
│       └── production/
│           ├── kustomization.yaml
│           └── patches/
├── docs/
│   ├── project_analysis.pdf
│   ├── system_diagnostics.json
│   └── ملف المشروع.zip
├── esp32/
│   ├── audio_processor.cpp
│   ├── audio_processor.h
│   ├── audio_stream.ino
│   ├── cloud_communication.ino
│   ├── esp32_hardware_analyzer.ino
│   ├── main.ino
│   ├── speaker_controller.ino
│   ├── teddy_bear_main.ino
│   ├── wake_word_detector.ino
│   ├── wifi_manager.ino
│   └── [+5 more files]
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json
│   │   └── offline.html
│   ├── src/
│   │   ├── architecture/
│   │   │   ├── application/
│   │   │   ├── dependency-injection/
│   │   │   ├── domain/
│   │   │   ├── infrastructure/
│   │   │   ├── presentation/
│   │   │   └── index.js
│   │   ├── components/
│   │   │   ├── Conversation.js
│   │   │   ├── Dashboard.js
│   │   │   └── [+6 more components]
│   │   ├── contexts/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── utils/
│   │   ├── App.js
│   │   ├── index.js
│   │   └── serviceWorkerRegistration.js
│   └── package.json
├── hardware/
├── monitoring/
│   └── emergency/
│       ├── alertmanager/
│       ├── api/
│       ├── kubernetes/
│       ├── nginx/
│       ├── prometheus/
│       ├── scripts/
│       └── docker-compose.emergency.yml
├── observability/
│   ├── architecture/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   ├── orchestration/
│   │   └── presentation/
│   ├── alert-rules.yaml
│   ├── grafana-dashboards.json
│   ├── sli-slo-definitions.yaml
│   └── README.md
├── scripts/
│   ├── migration/
│   │   ├── ddd_architecture_analyzer.py
│   │   ├── ddd_structure_creator.py
│   │   └── quick_ddd_setup.py
│   ├── advanced_deep_analyzer.py
│   ├── advanced_directories_analyzer.py
│   ├── chaos_experiment_runner.py
│   └── [+48 more scripts]
├── src/
│   ├── adapters/
│   │   ├── edge/
│   │   │   ├── edge_ai_manager.py (41KB)
│   │   │   └── __init__.py
│   │   ├── inbound/
│   │   └── outbound/
│   ├── application/
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   │   ├── llm_base.py (3.2KB) ✨ NEW
│   │   │   │   ├── llm_openai_adapter.py (4.1KB) ✨ NEW
│   │   │   │   ├── llm_anthropic_adapter.py (4.3KB) ✨ NEW
│   │   │   │   ├── llm_google_adapter.py (4.2KB) ✨ NEW
│   │   │   │   ├── llm_service_factory.py (10KB) 🔄 UPDATED
│   │   │   │   ├── llm_split_manifest.json ✨ NEW
│   │   │   │   ├── main_service.py (39KB)
│   │   │   │   ├── emotion_service.py (22KB)
│   │   │   │   ├── openai_service.py (21KB)
│   │   │   │   ├── unified_ai_service.py (20KB)
│   │   │   │   ├── modern_ai_service.py (19KB)
│   │   │   │   ├── edge_ai_integration_service.py (22KB)
│   │   │   │   ├── emotion_analytics_service.py (16KB)
│   │   │   │   ├── emotion_history_service.py (15KB)
│   │   │   │   ├── ai_service_factory.py (13KB)
│   │   │   │   ├── response_generator.py (12KB)
│   │   │   │   ├── educational_content.py (11KB)
│   │   │   │   ├── refactored_ai_service.py (11KB)
│   │   │   │   ├── models/
│   │   │   │   ├── interfaces/
│   │   │   │   ├── analyzers/
│   │   │   │   └── __init__.py
│   │   │   └── core/
│   │   │       ├── data_cleanup_service.py (43KB)
│   │   │       ├── moderation_service.py (38KB)
│   │   │       ├── advanced_personalization_service.py (33KB)
│   │   │       ├── ar_vr_service.py (34KB)
│   │   │       ├── notification_service.py (28KB)
│   │   │       ├── streaming_service.py (26KB)
│   │   │       ├── synthesis_service.py (28KB)
│   │   │       ├── cache_integration_service.py (22KB)
│   │   │       ├── cloud_transcription_service.py (20KB)
│   │   │       ├── health_service.py (18KB)
│   │   │       ├── fallback_response_service.py (18KB)
│   │   │       ├── websocket_manager.py (17KB)
│   │   │       └── [+30 more services]
│   │   ├── accessibility/
│   │   ├── cleanup/
│   │   ├── commands/
│   │   ├── emotion/
│   │   ├── events/
│   │   ├── interfaces/
│   │   ├── memory/
│   │   ├── patterns/
│   │   ├── queries/
│   │   ├── use_cases/
│   │   ├── health_monitoring.py
│   │   └── __init__.py
│   ├── compliance/
│   │   ├── alerts/
│   │   ├── checkers/
│   │   ├── managers/
│   │   ├── reports/
│   │   ├── audit_logger.py
│   │   ├── automated_compliance.py
│   │   └── compliance_demo.py
│   ├── core/
│   │   ├── domain/
│   │   └── services/
│   ├── dashboards/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── dashboard-demo-runner.py
│   │   ├── dashboard-demo.tsx
│   │   └── executive-dashboard.tsx
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── child.py
│   │   │   ├── conversation.py
│   │   │   ├── parent.py
│   │   │   ├── audio.py
│   │   │   ├── emotion.py
│   │   │   └── [+14 more entities]
│   │   ├── value_objects/
│   │   │   ├── child_id.py
│   │   │   ├── conversation_id.py
│   │   │   ├── emotion_score.py
│   │   │   └── [+5 more value objects]
│   │   ├── services/
│   │   ├── child/
│   │   ├── audio/
│   │   ├── emotion/
│   │   ├── memory/
│   │   ├── streaming/
│   │   ├── cleanup/
│   │   ├── reporting/
│   │   ├── exceptions/
│   │   ├── stories/
│   │   ├── behavioral_analyzer.py
│   │   ├── analytics.py
│   │   └── __init__.py
│   ├── edge/
│   │   ├── device_manager.py
│   │   ├── edge_orchestrator.py
│   │   └── edge_processor.py
│   ├── infrastructure/
│   │   ├── external_services/
│   │   │   ├── openai/
│   │   │   ├── anthropic/
│   │   │   ├── google/
│   │   │   ├── mock/
│   │   │   └── [+19 more external services]
│   │   ├── security/
│   │   │   └── [+29 security files]
│   │   ├── persistence/
│   │   │   ├── repositories/
│   │   │   └── [+5 persistence files]
│   │   ├── caching/
│   │   ├── messaging/
│   │   ├── monitoring/
│   │   ├── observability/
│   │   ├── graphql/
│   │   ├── emotion/
│   │   ├── audio/
│   │   ├── child/
│   │   ├── esp32/
│   │   ├── decorators/
│   │   ├── exception_handling/
│   │   ├── modern_container.py
│   │   ├── database.py
│   │   ├── cloud_server_launcher.py (34KB)
│   │   ├── parent_mobile_app_simulator.py (32KB)
│   │   ├── esp32_production_simulator.py (28KB)
│   │   └── complete_system_launcher.py (23KB)
│   ├── ml/
│   │   ├── continuous_learning/
│   │   ├── deployment/
│   │   └── pipelines/
│   ├── presentation/
│   │   ├── api/
│   │   ├── grpc/
│   │   ├── ui/
│   │   ├── services/
│   │   ├── enterprise_dashboard.py
│   │   └── enterprise_dashboard_refactored.py
│   ├── simulators/
│   │   ├── esp32_production_simulator.py
│   │   ├── esp32_simple_simulator.py
│   │   └── __init__.py
│   ├── testing/
│   │   ├── code_analyzer.py
│   │   ├── coverage_tracker.py
│   │   └── [+5 testing files]
│   ├── main.py (20KB)
│   ├── setup.py
│   ├── wsgi.py
│   └── __init__.py
├── tests/
│   ├── unit/
│   │   ├── ui/
│   │   │   ├── widgets/
│   │   │   ├── network/
│   │   │   └── audio/
│   │   ├── test_ai_safety_system.py
│   │   ├── test_bias_detection.py
│   │   ├── test_child_aggregate.py
│   │   ├── test_clean_container.py
│   │   ├── test_content_moderator.py
│   │   ├── test_conversation_repository.py
│   │   ├── test_distributed_processor.py
│   │   ├── test_edge_ai_manager.py
│   │   ├── test_emotion_analyzer.py
│   │   ├── test_graphql_federation.py
│   │   ├── test_homomorphic_encryption.py
│   │   ├── test_multi_layer_cache.py
│   │   ├── test_security_solutions.py
│   │   ├── test_voice_service.py
│   │   └── [+14 more unit tests]
│   ├── integration/
│   │   ├── test_ai_service_integration.py
│   │   ├── test_conversation_flow.py
│   │   └── test_voice_api_integration.py
│   ├── e2e/
│   │   ├── test_full_journey.py
│   │   ├── test_mobile_experience.py
│   │   └── playwright.config.js
│   ├── load/
│   │   ├── locustfile.py
│   │   ├── test_concurrent_users.py
│   │   └── test_load_performance.py
│   ├── security/
│   │   ├── test_child_protection_comprehensive.py
│   │   ├── test_child_safety_comprehensive.py
│   │   └── test_performance_critical.py
│   ├── performance/
│   │   └── test_system_performance.py
│   ├── framework/
│   │   ├── base.py
│   │   ├── bdd.py
│   │   └── __init__.py
│   ├── enhanced_testing/
│   ├── auto_generated/
│   ├── conftest.py
│   ├── test_validator.py
│   ├── test_integration.py
│   ├── test_exception_handling.py
│   ├── test_basic_functionality.py
│   ├── ai_test_demo.py
│   └── ai_test_generator.py
├── .env.template
├── .gitignore
├── .pre-commit-config.yaml
├── ARCHITECTURE.md
├── docker-compose.kafka.yml
├── docker-compose.vault.yml
├── FINAL_CLEANUP_REPORT.md
├── FINAL_PROJECT_STATUS.md
├── PROJECT_STRUCTURE_REPORT.md
├── SPLITTING_SUCCESS_REPORT.md ✨ NEW
├── pytest.ini
├── README.md
├── requirements.txt
├── requirements-security.txt
└── requirements_enhanced.txt
```

## 📊 إحصائيات المشروع

```
📁 Total Directories: ~85
📄 Total Files: ~350+
🐍 Python Files: ~95
⚛️ JavaScript/React: ~15
🔧 C++/Arduino: ~8
📋 Config/JSON: ~12
📄 Documentation: ~6

🎯 Core Focus Areas:
├── AI Services (25 files)
├── Infrastructure (40 files)
├── Domain Logic (20 files)
├── Tests (35 files)
└── Configuration (15 files)
```

## ✨ الملفات الجديدة (بعد التقسيم)

```
src/application/services/ai/
├── ✅ llm_base.py (3.2KB) - NEW
├── ✅ llm_openai_adapter.py (4.1KB) - NEW
├── ✅ llm_anthropic_adapter.py (4.3KB) - NEW
├── ✅ llm_google_adapter.py (4.2KB) - NEW
├── 🔄 llm_service_factory.py (10KB) - UPDATED
└── ✅ llm_split_manifest.json (896B) - NEW
``` 