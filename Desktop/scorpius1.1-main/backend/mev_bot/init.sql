-- MevGuardian Database Schema
-- Initialize the database with required tables for threats, simulations, and metrics

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Threats table
CREATE TABLE IF NOT EXISTS threats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    threat_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    transaction_hash VARCHAR(66),
    block_number BIGINT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Simulations table
CREATE TABLE IF NOT EXISTS simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    profit_usd DECIMAL(18, 8),
    gas_used BIGINT,
    success_probability DECIMAL(5, 4),
    execution_time_ms INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Honeypot scans table
CREATE TABLE IF NOT EXISTS honeypot_scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contract_address VARCHAR(42) NOT NULL,
    is_honeypot BOOLEAN,
    risk_level VARCHAR(20),
    reasons TEXT[],
    confidence_score DECIMAL(5, 4),
    scanned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Forensic analyses table
CREATE TABLE IF NOT EXISTS forensic_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id VARCHAR(100) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    findings TEXT,
    severity VARCHAR(20),
    recommendations TEXT,
    evidence_links TEXT[],
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Metrics table for aggregated data
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(50) NOT NULL,
    value DECIMAL(18, 8) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Bot operations log
CREATE TABLE IF NOT EXISTS operations_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operation_type VARCHAR(50) NOT NULL,
    mode VARCHAR(20) NOT NULL, -- 'attack' or 'guardian'
    status VARCHAR(20) NOT NULL,
    details JSONB,
    profit_usd DECIMAL(18, 8),
    gas_used BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_threats_type_severity ON threats(threat_type, severity);
CREATE INDEX IF NOT EXISTS idx_threats_detected_at ON threats(detected_at);
CREATE INDEX IF NOT EXISTS idx_threats_status ON threats(status);

CREATE INDEX IF NOT EXISTS idx_simulations_type_status ON simulations(simulation_type, status);
CREATE INDEX IF NOT EXISTS idx_simulations_created_at ON simulations(created_at);

CREATE INDEX IF NOT EXISTS idx_honeypot_address ON honeypot_scans(contract_address);
CREATE INDEX IF NOT EXISTS idx_honeypot_scanned_at ON honeypot_scans(scanned_at);

CREATE INDEX IF NOT EXISTS idx_forensic_incident ON forensic_analyses(incident_id);
CREATE INDEX IF NOT EXISTS idx_forensic_type ON forensic_analyses(analysis_type);

CREATE INDEX IF NOT EXISTS idx_metrics_type_timestamp ON metrics(metric_type, timestamp);

CREATE INDEX IF NOT EXISTS idx_operations_mode_type ON operations_log(mode, operation_type);
CREATE INDEX IF NOT EXISTS idx_operations_created_at ON operations_log(created_at);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_threats_updated_at BEFORE UPDATE ON threats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
