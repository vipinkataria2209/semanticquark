-- EPA Air Quality Monitoring System Database Schema
-- Validation dataset for semantic layer framework
-- 10 tables, 15,000+ records

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS compliance_reports CASCADE;
DROP TABLE IF EXISTS sensor_network_members CASCADE;
DROP TABLE IF EXISTS sensor_networks CASCADE;
DROP TABLE IF EXISTS air_quality_index CASCADE;
DROP TABLE IF EXISTS maintenance_logs CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS measurements CASCADE;
DROP TABLE IF EXISTS sensors CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- Create organizations table
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    org_code VARCHAR(50) UNIQUE NOT NULL,
    org_name VARCHAR(200) NOT NULL,
    org_type VARCHAR(50),  -- federal, state, local, research, commercial
    contact_email VARCHAR(200),
    contact_phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create locations table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    location_code VARCHAR(50) UNIQUE NOT NULL,
    location_name VARCHAR(200) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    zip_code VARCHAR(10),
    region VARCHAR(50),  -- Northeast, Midwest, South, West
    timezone VARCHAR(50) DEFAULT 'America/Los_Angeles',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sensors table
CREATE TABLE sensors (
    id SERIAL PRIMARY KEY,
    sensor_code VARCHAR(50) UNIQUE NOT NULL,
    sensor_name VARCHAR(200),
    sensor_type VARCHAR(50),  -- PM2.5, PM10, Ozone, NO2, CO, SO2
    location_id INTEGER REFERENCES locations(id),
    organization_id INTEGER REFERENCES organizations(id),
    installation_date DATE,
    last_calibration_date DATE,
    status VARCHAR(20) DEFAULT 'active',  -- active, inactive, maintenance, offline
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    elevation_meters INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create measurements table
CREATE TABLE measurements (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER REFERENCES sensors(id),
    measurement_type VARCHAR(50),  -- PM2.5, PM10, Ozone, NO2, CO, SO2
    value DECIMAL(10, 3),
    unit VARCHAR(20),  -- µg/m³, ppm, ppb
    quality_flag VARCHAR(20) DEFAULT 'valid',  -- valid, invalid, questionable
    recorded_at TIMESTAMP NOT NULL,
    temperature_celsius DECIMAL(5, 2),
    humidity_percent DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create alerts table
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER REFERENCES sensors(id),
    measurement_id INTEGER REFERENCES measurements(id),
    alert_type VARCHAR(50),  -- unhealthy, hazardous, equipment_fault
    severity VARCHAR(20),  -- low, medium, high, critical
    threshold_value DECIMAL(10, 3),
    actual_value DECIMAL(10, 3),
    triggered_at TIMESTAMP NOT NULL,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',  -- active, acknowledged, resolved
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create maintenance_logs table
CREATE TABLE maintenance_logs (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER REFERENCES sensors(id),
    maintenance_type VARCHAR(50),  -- calibration, repair, replacement, cleaning
    technician_name VARCHAR(200),
    description TEXT,
    performed_at TIMESTAMP NOT NULL,
    next_maintenance_due DATE,
    cost DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create air_quality_index table
CREATE TABLE air_quality_index (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id),
    measurement_type VARCHAR(50),
    aqi_value INTEGER,
    aqi_category VARCHAR(50),  -- Good, Moderate, Unhealthy for Sensitive Groups, Unhealthy, Very Unhealthy, Hazardous
    calculated_at TIMESTAMP NOT NULL,
    based_on_measurement_id INTEGER REFERENCES measurements(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sensor_networks table
CREATE TABLE sensor_networks (
    id SERIAL PRIMARY KEY,
    network_code VARCHAR(50) UNIQUE NOT NULL,
    network_name VARCHAR(200) NOT NULL,
    description TEXT,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sensor_network_members table (junction table)
CREATE TABLE sensor_network_members (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER REFERENCES sensors(id),
    network_id INTEGER REFERENCES sensor_networks(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sensor_id, network_id)
);

-- Create compliance_reports table
CREATE TABLE compliance_reports (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    location_id INTEGER REFERENCES locations(id),
    report_type VARCHAR(50),  -- monthly, quarterly, annual
    report_period_start DATE,
    report_period_end DATE,
    generated_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',  -- draft, submitted, approved
    file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_sensors_location ON sensors(location_id);
CREATE INDEX idx_sensors_organization ON sensors(organization_id);
CREATE INDEX idx_sensors_status ON sensors(status);
CREATE INDEX idx_sensors_type ON sensors(sensor_type);
CREATE INDEX idx_measurements_sensor ON measurements(sensor_id);
CREATE INDEX idx_measurements_recorded_at ON measurements(recorded_at);
CREATE INDEX idx_measurements_type ON measurements(measurement_type);
CREATE INDEX idx_alerts_sensor ON alerts(sensor_id);
CREATE INDEX idx_alerts_triggered_at ON alerts(triggered_at);
CREATE INDEX idx_aqi_location ON air_quality_index(location_id);
CREATE INDEX idx_aqi_calculated_at ON air_quality_index(calculated_at);

-- Insert sample data

-- Insert organizations (45 records)
INSERT INTO organizations (org_code, org_name, org_type, contact_email) VALUES
('EPA', 'Environmental Protection Agency', 'federal', 'contact@epa.gov'),
('CARB', 'California Air Resources Board', 'state', 'info@arb.ca.gov'),
('TCEQ', 'Texas Commission on Environmental Quality', 'state', 'info@tceq.texas.gov'),
('NYSDEC', 'New York State Department of Environmental Conservation', 'state', 'info@dec.ny.gov'),
('AQMD', 'South Coast Air Quality Management District', 'local', 'info@aqmd.gov'),
('RESEARCH-01', 'Stanford Environmental Research Institute', 'research', 'research@stanford.edu'),
('RESEARCH-02', 'MIT Air Quality Lab', 'research', 'airlab@mit.edu'),
('COMMERCIAL-01', 'Air Quality Solutions Inc', 'commercial', 'sales@aqsolutions.com'),
('COMMERCIAL-02', 'Environmental Monitoring Corp', 'commercial', 'info@envmonitor.com');

-- Insert more organizations to reach 45
INSERT INTO organizations (org_code, org_name, org_type)
SELECT 
    'ORG-' || generate_series(10, 45),
    'Organization ' || generate_series(10, 45),
    CASE (random() * 4)::int
        WHEN 0 THEN 'federal'
        WHEN 1 THEN 'state'
        WHEN 2 THEN 'local'
        WHEN 3 THEN 'research'
        ELSE 'commercial'
    END;

-- Insert locations (150 records)
INSERT INTO locations (location_code, location_name, city, state, country, region) VALUES
('CA-LA-001', 'Los Angeles Downtown', 'Los Angeles', 'California', 'USA', 'West'),
('CA-SF-001', 'San Francisco Bay Area', 'San Francisco', 'California', 'USA', 'West'),
('CA-SD-001', 'San Diego Coastal', 'San Diego', 'California', 'USA', 'West'),
('TX-HOU-001', 'Houston Industrial', 'Houston', 'Texas', 'USA', 'South'),
('TX-DAL-001', 'Dallas Metro', 'Dallas', 'Texas', 'USA', 'South'),
('NY-NYC-001', 'New York City Manhattan', 'New York', 'New York', 'USA', 'Northeast'),
('NY-NYC-002', 'New York City Brooklyn', 'New York', 'New York', 'USA', 'Northeast'),
('IL-CHI-001', 'Chicago Downtown', 'Chicago', 'Illinois', 'USA', 'Midwest'),
('FL-MIA-001', 'Miami Beach', 'Miami', 'Florida', 'USA', 'South'),
('WA-SEA-001', 'Seattle Urban', 'Seattle', 'Washington', 'USA', 'West');

-- Insert more locations to reach 150
INSERT INTO locations (location_code, location_name, city, state, country, region)
SELECT 
    state_abbr || '-' || city_abbr || '-' || LPAD(series::text, 3, '0'),
    city_name || ' Station ' || series,
    city_name,
    state_name,
    'USA',
    region_name
FROM (
    SELECT 
        generate_series(11, 150) as series,
        CASE (random() * 9)::int
            WHEN 0 THEN ('CA', 'California', 'Los Angeles', 'West')
            WHEN 1 THEN ('TX', 'Texas', 'Houston', 'South')
            WHEN 2 THEN ('NY', 'New York', 'New York', 'Northeast')
            WHEN 3 THEN ('IL', 'Illinois', 'Chicago', 'Midwest')
            WHEN 4 THEN ('FL', 'Florida', 'Miami', 'South')
            WHEN 5 THEN ('WA', 'Washington', 'Seattle', 'West')
            WHEN 6 THEN ('AZ', 'Arizona', 'Phoenix', 'West')
            WHEN 7 THEN ('CO', 'Colorado', 'Denver', 'West')
            ELSE ('GA', 'Georgia', 'Atlanta', 'South')
        END as location_data
) t, LATERAL (
    SELECT 
        location_data[1] as state_abbr,
        location_data[2] as state_name,
        location_data[3] as city_name,
        location_data[4] as region_name
) loc;

-- Insert sensors (1,200 records)
INSERT INTO sensors (sensor_code, sensor_name, sensor_type, location_id, organization_id, 
                     installation_date, status, latitude, longitude, elevation_meters)
SELECT 
    'SENSOR-' || LPAD(series::text, 6, '0'),
    'Sensor ' || series,
    CASE (random() * 5)::int
        WHEN 0 THEN 'PM2.5'
        WHEN 1 THEN 'PM10'
        WHEN 2 THEN 'Ozone'
        WHEN 3 THEN 'NO2'
        WHEN 4 THEN 'CO'
        ELSE 'SO2'
    END,
    (random() * 149 + 1)::int,
    (random() * 44 + 1)::int,
    '2023-01-01'::date + (random() * 730)::int,
    CASE (random() * 3)::int
        WHEN 0 THEN 'active'
        WHEN 1 THEN 'active'
        WHEN 2 THEN 'maintenance'
        ELSE 'inactive'
    END,
    34.0522 + (random() * 10 - 5),  -- Latitude around California
    -118.2437 + (random() * 10 - 5),  -- Longitude around California
    (random() * 2000)::int
FROM generate_series(1, 1200) series;

-- Insert measurements (8,500 records)
INSERT INTO measurements (sensor_id, measurement_type, value, unit, quality_flag, 
                          recorded_at, temperature_celsius, humidity_percent)
SELECT 
    (random() * 1199 + 1)::int,
    CASE (random() * 5)::int
        WHEN 0 THEN 'PM2.5'
        WHEN 1 THEN 'PM10'
        WHEN 2 THEN 'Ozone'
        WHEN 3 THEN 'NO2'
        WHEN 4 THEN 'CO'
        ELSE 'SO2'
    END,
    CASE 
        WHEN (random() * 5)::int = 0 THEN (random() * 200 + 10)::decimal(10,3)  -- PM2.5/PM10: 10-210 µg/m³
        WHEN (random() * 5)::int = 1 THEN (random() * 300 + 20)::decimal(10,3)  -- PM10: 20-320 µg/m³
        WHEN (random() * 5)::int = 2 THEN (random() * 200 + 50)::decimal(10,3)  -- Ozone: 50-250 ppb
        WHEN (random() * 5)::int = 3 THEN (random() * 100 + 10)::decimal(10,3)  -- NO2: 10-110 ppb
        WHEN (random() * 5)::int = 4 THEN (random() * 5 + 0.5)::decimal(10,3)  -- CO: 0.5-5.5 ppm
        ELSE (random() * 50 + 5)::decimal(10,3)  -- SO2: 5-55 ppb
    END,
    CASE (random() * 2)::int
        WHEN 0 THEN 'µg/m³'
        WHEN 1 THEN 'ppb'
        ELSE 'ppm'
    END,
    CASE (random() * 9)::int
        WHEN 0 THEN 'invalid'
        WHEN 1 THEN 'questionable'
        ELSE 'valid'
    END,
    '2023-01-01'::timestamp + (random() * 730 * 24 * 3600)::int * interval '1 second',
    (random() * 40 - 10)::decimal(5,2),  -- Temperature: -10 to 30°C
    (random() * 80 + 20)::decimal(5,2)  -- Humidity: 20-100%
FROM generate_series(1, 8500) series;

-- Insert alerts (320 records)
INSERT INTO alerts (sensor_id, measurement_id, alert_type, severity, threshold_value, 
                   actual_value, triggered_at, status)
SELECT 
    (random() * 1199 + 1)::int,
    (random() * 8499 + 1)::int,
    CASE (random() * 2)::int
        WHEN 0 THEN 'unhealthy'
        WHEN 1 THEN 'hazardous'
        ELSE 'equipment_fault'
    END,
    CASE (random() * 3)::int
        WHEN 0 THEN 'low'
        WHEN 1 THEN 'medium'
        WHEN 2 THEN 'high'
        ELSE 'critical'
    END,
    (random() * 100 + 50)::decimal(10,3),
    (random() * 150 + 100)::decimal(10,3),
    '2023-01-01'::timestamp + (random() * 730 * 24 * 3600)::int * interval '1 second',
    CASE (random() * 2)::int
        WHEN 0 THEN 'active'
        WHEN 1 THEN 'acknowledged'
        ELSE 'resolved'
    END
FROM generate_series(1, 320) series;

-- Insert maintenance_logs (180 records)
INSERT INTO maintenance_logs (sensor_id, maintenance_type, technician_name, description, 
                              performed_at, next_maintenance_due, cost)
SELECT 
    (random() * 1199 + 1)::int,
    CASE (random() * 3)::int
        WHEN 0 THEN 'calibration'
        WHEN 1 THEN 'repair'
        WHEN 2 THEN 'cleaning'
        ELSE 'replacement'
    END,
    'Technician ' || (random() * 50 + 1)::int,
    'Maintenance performed',
    '2023-01-01'::timestamp + (random() * 730 * 24 * 3600)::int * interval '1 second',
    '2024-12-31'::date + (random() * 365)::int,
    (random() * 5000 + 100)::decimal(10,2)
FROM generate_series(1, 180) series;

-- Insert air_quality_index (2,100 records)
INSERT INTO air_quality_index (location_id, measurement_type, aqi_value, aqi_category, 
                               calculated_at, based_on_measurement_id)
SELECT 
    (random() * 149 + 1)::int,
    CASE (random() * 5)::int
        WHEN 0 THEN 'PM2.5'
        WHEN 1 THEN 'PM10'
        WHEN 2 THEN 'Ozone'
        WHEN 3 THEN 'NO2'
        ELSE 'CO'
    END,
    (random() * 300 + 0)::int,  -- AQI: 0-300
    CASE 
        WHEN (random() * 300)::int < 50 THEN 'Good'
        WHEN (random() * 300)::int < 100 THEN 'Moderate'
        WHEN (random() * 300)::int < 150 THEN 'Unhealthy for Sensitive Groups'
        WHEN (random() * 300)::int < 200 THEN 'Unhealthy'
        WHEN (random() * 300)::int < 300 THEN 'Very Unhealthy'
        ELSE 'Hazardous'
    END,
    '2023-01-01'::timestamp + (random() * 730 * 24 * 3600)::int * interval '1 second',
    (random() * 8499 + 1)::int
FROM generate_series(1, 2100) series;

-- Insert sensor_networks (25 records)
INSERT INTO sensor_networks (network_code, network_name, description, region)
SELECT 
    'NET-' || LPAD(series::text, 3, '0'),
    'Network ' || series,
    'Sensor network description',
    CASE (random() * 3)::int
        WHEN 0 THEN 'West'
        WHEN 1 THEN 'South'
        WHEN 2 THEN 'Northeast'
        ELSE 'Midwest'
    END
FROM generate_series(1, 25) series;

-- Insert sensor_network_members (1,200 records - one per sensor)
INSERT INTO sensor_network_members (sensor_id, network_id)
SELECT 
    series,
    (random() * 24 + 1)::int
FROM generate_series(1, 1200) series;

-- Insert compliance_reports (95 records)
INSERT INTO compliance_reports (organization_id, location_id, report_type, 
                                report_period_start, report_period_end, generated_at, status)
SELECT 
    (random() * 44 + 1)::int,
    (random() * 149 + 1)::int,
    CASE (random() * 2)::int
        WHEN 0 THEN 'monthly'
        WHEN 1 THEN 'quarterly'
        ELSE 'annual'
    END,
    '2023-01-01'::date + (random() * 600)::int,
    '2023-01-01'::date + (random() * 600 + 30)::int,
    '2023-01-01'::timestamp + (random() * 730 * 24 * 3600)::int * interval '1 second',
    CASE (random() * 2)::int
        WHEN 0 THEN 'draft'
        WHEN 1 THEN 'submitted'
        ELSE 'approved'
    END
FROM generate_series(1, 95) series;

-- Update some sensors with calibration dates
UPDATE sensors 
SET last_calibration_date = installation_date + (random() * 365)::int
WHERE random() > 0.7;

-- Verify data
SELECT 
    'organizations' as table_name, COUNT(*) as record_count FROM organizations
UNION ALL
SELECT 'locations', COUNT(*) FROM locations
UNION ALL
SELECT 'sensors', COUNT(*) FROM sensors
UNION ALL
SELECT 'measurements', COUNT(*) FROM measurements
UNION ALL
SELECT 'alerts', COUNT(*) FROM alerts
UNION ALL
SELECT 'maintenance_logs', COUNT(*) FROM maintenance_logs
UNION ALL
SELECT 'air_quality_index', COUNT(*) FROM air_quality_index
UNION ALL
SELECT 'sensor_networks', COUNT(*) FROM sensor_networks
UNION ALL
SELECT 'sensor_network_members', COUNT(*) FROM sensor_network_members
UNION ALL
SELECT 'compliance_reports', COUNT(*) FROM compliance_reports;

