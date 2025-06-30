-- Task 7: Create parent_reports table for advanced progress analysis
-- Migration for storing LLM-generated progress analysis and recommendations

CREATE TABLE IF NOT EXISTS parent_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metrics TEXT NOT NULL,  -- JSON containing ProgressMetrics
    recommendations TEXT NOT NULL,  -- JSON containing LLMRecommendations
    analysis_version VARCHAR(50) NOT NULL DEFAULT 'Task7_v1.0',
    llm_used BOOLEAN DEFAULT FALSE,
    urgency_level INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_parent_reports_child_id ON parent_reports(child_id);
CREATE INDEX IF NOT EXISTS idx_parent_reports_generated_at ON parent_reports(generated_at);
CREATE INDEX IF NOT EXISTS idx_parent_reports_urgency ON parent_reports(urgency_level);
CREATE INDEX IF NOT EXISTS idx_parent_reports_version ON parent_reports(analysis_version);

-- Insert sample data for testing (optional)
-- INSERT INTO parent_reports (child_id, metrics, recommendations, analysis_version, llm_used)
-- VALUES (
--     1, 
--     '{"child_id": 1, "total_unique_words": 25, "vocabulary_complexity_score": 0.6}',
--     '[{"category": "learning", "recommendation": "Increase reading time", "priority_level": 3}]',
--     'Task7_v1.0',
--     true
-- ); 