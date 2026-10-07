-- Automated Data Analysis Platform MySQL 8 Schema
-- Database Creation
CREATE DATABASE IF NOT EXISTS automated_da CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE automated_da;

-- 1. Datasets Table
CREATE TABLE IF NOT EXISTS datasets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    row_count INT DEFAULT 0,
    column_count INT DEFAULT 0,
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_file_type (file_type),
    INDEX idx_upload_timestamp (upload_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Dataset Columns Table
CREATE TABLE IF NOT EXISTS dataset_columns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id INT NOT NULL,
    column_name VARCHAR(255) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    inferred_type VARCHAR(100) NOT NULL,
    is_nullable BOOLEAN DEFAULT TRUE,
    null_count INT DEFAULT 0,
    unique_count INT DEFAULT 0,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
    INDEX idx_dataset_id (dataset_id),
    INDEX idx_inferred_type (inferred_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Analysis Results Table
CREATE TABLE IF NOT EXISTS analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id INT NOT NULL,
    analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    quality_score FLOAT DEFAULT 0.0,
    data_quality_json JSON,
    numerical_stats_json JSON,
    categorical_stats_json JSON,
    correlation_matrix_json JSON,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
    INDEX idx_analysis_dataset (dataset_id),
    INDEX idx_analysis_timestamp (analysis_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Generated Charts Table
CREATE TABLE IF NOT EXISTS generated_charts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id INT NOT NULL,
    analysis_id INT NOT NULL,
    chart_type VARCHAR(100) NOT NULL,
    chart_title VARCHAR(255) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    chart_metadata_json JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE,
    INDEX idx_chart_dataset (dataset_id),
    INDEX idx_chart_analysis (analysis_id),
    INDEX idx_chart_type (chart_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id INT NOT NULL,
    analysis_id INT NOT NULL,
    report_title VARCHAR(255) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE,
    INDEX idx_report_dataset (dataset_id),
    INDEX idx_report_analysis (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
