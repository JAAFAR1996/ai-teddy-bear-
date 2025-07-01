"""
🔧 Kafka Configuration Management
=================================

Enterprise-grade Kafka configuration for AI Teddy Bear event streaming
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class CompressionType(Enum):
    """Kafka compression types"""

    NONE = "none"
    GZIP = "gzip"
    SNAPPY = "snappy"
    LZ4 = "lz4"
    ZSTD = "zstd"


class AcksConfig(Enum):
    """Producer acknowledgment configuration"""

    NONE = "0"  # Fire and forget
    LEADER = "1"  # Wait for leader acknowledgment
    ALL = "all"  # Wait for all in-sync replicas


@dataclass(frozen=True)
class KafkaProducerConfig:
    """Producer configuration for high-performance event publishing"""

    # Connection settings
    bootstrap_servers: List[str] = field(default_factory=lambda: ["localhost:9092"])
    client_id: str = "teddy-producer"

    # Performance settings
    batch_size: int = 32768  # 32KB batch size
    linger_ms: int = 100  # Wait 100ms for batching
    buffer_memory: int = 67108864  # 64MB buffer
    compression_type: CompressionType = CompressionType.SNAPPY

    # Reliability settings
    acks: AcksConfig = AcksConfig.ALL
    retries: int = 3
    retry_backoff_ms: int = 1000
    request_timeout_ms: int = 30000
    delivery_timeout_ms: int = 120000

    # Message settings
    max_request_size: int = 1048576  # 1MB

    # Idempotence for exactly-once semantics
    enable_idempotence: bool = True

    # Security settings (for production)
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None

    def to_kafka_config(self) -> Dict[str, Any]:
        """Convert to kafka-python producer config"""
        return {
            "bootstrap_servers": self.bootstrap_servers,
            "client_id": self.client_id,
            "batch_size": self.batch_size,
            "linger_ms": self.linger_ms,
            "buffer_memory": self.buffer_memory,
            "compression_type": self.compression_type.value,
            "acks": self.acks.value,
            "retries": self.retries,
            "retry_backoff_ms": self.retry_backoff_ms,
            "request_timeout_ms": self.request_timeout_ms,
            "delivery_timeout_ms": self.delivery_timeout_ms,
            "max_request_size": self.max_request_size,
            "enable_idempotence": self.enable_idempotence,
            "security_protocol": self.security_protocol,
        }


@dataclass(frozen=True)
class KafkaConsumerConfig:
    """Consumer configuration for reliable event processing"""

    # Connection settings
    bootstrap_servers: List[str] = field(default_factory=lambda: ["localhost:9092"])
    client_id: str = "teddy-consumer"
    group_id: str = "teddy-consumer-group"

    # Offset management
    auto_offset_reset: str = "earliest"  # Start from beginning if no offset
    enable_auto_commit: bool = False  # Manual commit for reliability
    auto_commit_interval_ms: int = 5000

    # Session management
    session_timeout_ms: int = 30000
    heartbeat_interval_ms: int = 10000
    max_poll_interval_ms: int = 300000  # 5 minutes

    # Performance settings
    fetch_min_bytes: int = 1024  # 1KB minimum fetch
    fetch_max_wait_ms: int = 500  # Wait 500ms for batch
    max_partition_fetch_bytes: int = 1048576  # 1MB per partition
    max_poll_records: int = 500  # Process 500 records per poll

    # Message processing
    check_crcs: bool = True  # Verify message integrity

    # Security settings (for production)
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None

    def to_kafka_config(self) -> Dict[str, Any]:
        """Convert to kafka-python consumer config"""
        return {
            "bootstrap_servers": self.bootstrap_servers,
            "client_id": self.client_id,
            "group_id": self.group_id,
            "auto_offset_reset": self.auto_offset_reset,
            "enable_auto_commit": self.enable_auto_commit,
            "auto_commit_interval_ms": self.auto_commit_interval_ms,
            "session_timeout_ms": self.session_timeout_ms,
            "heartbeat_interval_ms": self.heartbeat_interval_ms,
            "max_poll_interval_ms": self.max_poll_interval_ms,
            "fetch_min_bytes": self.fetch_min_bytes,
            "fetch_max_wait_ms": self.fetch_max_wait_ms,
            "max_partition_fetch_bytes": self.max_partition_fetch_bytes,
            "max_poll_records": self.max_poll_records,
            "check_crcs": self.check_crcs,
            "security_protocol": self.security_protocol,
        }


@dataclass(frozen=True)
class TopicConfig:
    """Kafka topic configuration"""

    name: str
    partitions: int = 3
    replication_factor: int = 1
    retention_ms: int = 604800000  # 7 days default
    cleanup_policy: str = "delete"
    compression_type: str = "snappy"
    max_message_bytes: int = 1000000  # 1MB

    def to_topic_config(self) -> Dict[str, str]:
        """Convert to Kafka topic config"""
        return {
            "retention.ms": str(self.retention_ms),
            "cleanup.policy": self.cleanup_policy,
            "compression.type": self.compression_type,
            "max.message.bytes": str(self.max_message_bytes),
        }


class KafkaTopics:
    """Centralized topic definitions for AI Teddy Bear system"""

    # Child Events Topics
    CHILD_REGISTERED = TopicConfig(name="child.registered", partitions=3, retention_ms=2592000000)  # 30 days

    CHILD_PROFILE_UPDATED = TopicConfig(name="child.profile-updated", partitions=3, retention_ms=2592000000)  # 30 days

    CHILD_SAFETY_VIOLATION = TopicConfig(
        name="child.safety-violation", partitions=3, retention_ms=7776000000  # 90 days - important for compliance
    )

    CHILD_MILESTONE_ACHIEVED = TopicConfig(
        name="child.milestone-achieved", partitions=3, retention_ms=31536000000  # 365 days - long-term tracking
    )

    # Conversation Events Topics
    CONVERSATION_STARTED = TopicConfig(
        name="conversation.started", partitions=6, retention_ms=604800000  # Higher throughput expected  # 7 days
    )

    CONVERSATION_ENDED = TopicConfig(name="conversation.ended", partitions=6, retention_ms=604800000)  # 7 days

    CONVERSATION_ESCALATED = TopicConfig(
        name="conversation.escalated", partitions=3, retention_ms=7776000000  # 90 days - critical events
    )

    MESSAGE_RECEIVED = TopicConfig(
        name="message.received", partitions=6, retention_ms=604800000  # High volume expected  # 7 days
    )

    RESPONSE_GENERATED = TopicConfig(name="response.generated", partitions=6, retention_ms=604800000)  # 7 days

    EMOTION_DETECTED = TopicConfig(
        name="emotion.detected", partitions=3, retention_ms=2592000000  # 30 days for analysis
    )

    # Analytics Topics
    USAGE_STATS = TopicConfig(name="analytics.usage-stats", partitions=3, retention_ms=7776000000)  # 90 days

    ENGAGEMENT_METRICS = TopicConfig(
        name="analytics.engagement-metrics", partitions=3, retention_ms=7776000000  # 90 days
    )

    # System Topics
    HEALTH_CHECK = TopicConfig(name="system.health-check", partitions=1, retention_ms=86400000)  # 1 day

    AUDIT_LOG = TopicConfig(name="system.audit-log", partitions=3, retention_ms=31536000000)  # 365 days - compliance

    # Dead Letter Queue
    DLQ_FAILED_EVENTS = TopicConfig(name="dlq.failed-events", partitions=1, retention_ms=2592000000)  # 30 days

    @classmethod
    def get_all_topics(cls) -> List[TopicConfig]:
        """Get all topic configurations"""
        return [
            cls.CHILD_REGISTERED,
            cls.CHILD_PROFILE_UPDATED,
            cls.CHILD_SAFETY_VIOLATION,
            cls.CHILD_MILESTONE_ACHIEVED,
            cls.CONVERSATION_STARTED,
            cls.CONVERSATION_ENDED,
            cls.CONVERSATION_ESCALATED,
            cls.MESSAGE_RECEIVED,
            cls.RESPONSE_GENERATED,
            cls.EMOTION_DETECTED,
            cls.USAGE_STATS,
            cls.ENGAGEMENT_METRICS,
            cls.HEALTH_CHECK,
            cls.AUDIT_LOG,
            cls.DLQ_FAILED_EVENTS,
        ]


class KafkaEnvironmentConfig:
    """Environment-specific Kafka configurations"""

    @staticmethod
    def development() -> tuple[KafkaProducerConfig, KafkaConsumerConfig]:
        """Development environment configuration"""
        producer_config = KafkaProducerConfig(
            bootstrap_servers=["localhost:9092"],
            client_id="teddy-dev-producer",
            batch_size=16384,  # Smaller batches for development
            linger_ms=10,  # Faster response for development
            acks=AcksConfig.LEADER,  # Faster acknowledgment
        )

        consumer_config = KafkaConsumerConfig(
            bootstrap_servers=["localhost:9092"],
            client_id="teddy-dev-consumer",
            group_id="teddy-dev-consumer-group",
            max_poll_records=100,  # Smaller batches for development
        )

        return producer_config, consumer_config

    @staticmethod
    def production() -> tuple[KafkaProducerConfig, KafkaConsumerConfig]:
        """Production environment configuration"""
        producer_config = KafkaProducerConfig(
            bootstrap_servers=os.getenv("KAFKA_BROKERS", "localhost:9092").split(","),
            client_id="teddy-prod-producer",
            batch_size=65536,  # Larger batches for throughput
            linger_ms=100,  # Balance between latency and throughput
            acks=AcksConfig.ALL,  # Maximum durability
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            sasl_username=os.getenv("KAFKA_SASL_USERNAME"),
            sasl_password=os.getenv("KAFKA_SASL_PASSWORD"),
        )

        consumer_config = KafkaConsumerConfig(
            bootstrap_servers=os.getenv("KAFKA_BROKERS", "localhost:9092").split(","),
            client_id="teddy-prod-consumer",
            group_id=os.getenv("KAFKA_CONSUMER_GROUP", "teddy-prod-consumer-group"),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            sasl_username=os.getenv("KAFKA_SASL_USERNAME"),
            sasl_password=os.getenv("KAFKA_SASL_PASSWORD"),
        )

        return producer_config, consumer_config

    @staticmethod
    def get_config_for_environment(env: str = None) -> tuple[KafkaProducerConfig, KafkaConsumerConfig]:
        """Get configuration based on environment"""
        if env is None:
            env = os.getenv("ENVIRONMENT", "development")

        if env.lower() == "production":
            return KafkaEnvironmentConfig.production()
        else:
            return KafkaEnvironmentConfig.development()


# Schema Registry Configuration
@dataclass(frozen=True)
class SchemaRegistryConfig:
    """Schema Registry configuration"""

    url: str = "http://localhost:8081"
    username: Optional[str] = None
    password: Optional[str] = None

    def to_config(self) -> Dict[str, Any]:
        """Convert to schema registry config"""
        config = {"url": self.url}
        if self.username and self.password:
            config.update(
                {
                    "basic.auth.credentials.source": "USER_INFO",
                    "basic.auth.user.info": f"{self.username}:{self.password}",
                }
            )
        return config


# Monitoring Configuration
@dataclass(frozen=True)
class KafkaMonitoringConfig:
    """Kafka monitoring and metrics configuration"""

    # JMX settings
    jmx_port: int = 9999
    enable_jmx: bool = True

    # Metrics reporting
    metrics_sample_window_ms: int = 30000
    metrics_num_samples: int = 2

    # Health check settings
    health_check_interval_seconds: int = 30
    connection_timeout_seconds: int = 10

    def get_jmx_opts(self) -> str:
        """Get JMX options for Kafka clients"""
        if not self.enable_jmx:
            return ""

        return (
            f"-Dcom.sun.management.jmxremote "
            f"-Dcom.sun.management.jmxremote.port={self.jmx_port} "
            f"-Dcom.sun.management.jmxremote.authenticate=false "
            f"-Dcom.sun.management.jmxremote.ssl=false"
        )


# Global configuration instance
KAFKA_CONFIG = KafkaEnvironmentConfig.get_config_for_environment()
SCHEMA_REGISTRY_CONFIG = SchemaRegistryConfig()
MONITORING_CONFIG = KafkaMonitoringConfig()
