# Requirements Document

## Introduction

This feature migrates the FarmMe application database from local PostgreSQL to Supabase cloud database. The goal is to enable data synchronization across multiple machines by using a centralized cloud database service. This will ensure all team members and deployment environments access the same data.

## Glossary

- **FarmMe System**: The smart farming recommendation application consisting of backend API and frontend interface
- **Local PostgreSQL**: The current PostgreSQL database running on localhost
- **Supabase**: A cloud-based PostgreSQL database service with built-in APIs and authentication
- **Database Schema**: The structure of tables, columns, and relationships in the database
- **Migration**: The process of transferring database schema and data from one system to another
- **Connection String**: A URL containing credentials and endpoint information for database access

## Requirements

### Requirement 1

**User Story:** As a developer, I want to migrate the database to Supabase, so that all team members can access the same data regardless of their machine

#### Acceptance Criteria

1. WHEN the system initializes, THE FarmMe System SHALL connect to the Supabase PostgreSQL database using the provided connection credentials
2. THE FarmMe System SHALL maintain all existing database tables and their schemas in the Supabase database
3. THE FarmMe System SHALL preserve all existing data during the migration process
4. THE FarmMe System SHALL use the Supabase connection string format: `postgresql://[user]:[password]@[host]:[port]/[database]`
5. WHERE the DATABASE_URL environment variable is set to Supabase credentials, THE FarmMe System SHALL connect to the cloud database instead of localhost

### Requirement 2

**User Story:** As a developer, I want to export existing data from local PostgreSQL, so that I can import it into Supabase without data loss

#### Acceptance Criteria

1. THE FarmMe System SHALL provide a script to export all table data from the local PostgreSQL database
2. THE FarmMe System SHALL export data in a format compatible with PostgreSQL import commands
3. THE FarmMe System SHALL include all tables: users, crop_predictions, chat_sessions, forecast_data, province_data, crop_prices, crop_characteristics, weather_data, economic_factors, and crop_cultivation
4. WHEN the export script completes, THE FarmMe System SHALL generate a SQL dump file containing all schema and data
5. THE FarmMe System SHALL validate that the export file is not corrupted before proceeding

### Requirement 3

**User Story:** As a developer, I want to configure the application to use Supabase, so that the backend and frontend can connect to the cloud database

#### Acceptance Criteria

1. THE FarmMe System SHALL update the DATABASE_URL environment variable in backend/.env to use Supabase connection string
2. THE FarmMe System SHALL maintain backward compatibility with local PostgreSQL for development purposes
3. WHEN the Supabase connection is configured, THE FarmMe System SHALL successfully create a database connection on application startup
4. THE FarmMe System SHALL log connection status indicating whether Supabase or local database is being used
5. WHERE connection to Supabase fails, THE FarmMe System SHALL provide clear error messages with troubleshooting guidance

### Requirement 4

**User Story:** As a developer, I want to import the existing data into Supabase, so that the application can continue working with historical data

#### Acceptance Criteria

1. THE FarmMe System SHALL provide a script to import the SQL dump file into Supabase database
2. WHEN the import script runs, THE FarmMe System SHALL create all necessary tables in Supabase if they do not exist
3. THE FarmMe System SHALL import all data records while maintaining referential integrity
4. WHEN the import completes, THE FarmMe System SHALL verify that record counts match between source and destination
5. IF import errors occur, THEN THE FarmMe System SHALL log detailed error messages and continue with remaining tables

### Requirement 5

**User Story:** As a developer, I want to verify the migration was successful, so that I can confirm the application works correctly with Supabase

#### Acceptance Criteria

1. THE FarmMe System SHALL provide a verification script to test database connectivity and data integrity
2. WHEN the verification script runs, THE FarmMe System SHALL query each table and report record counts
3. THE FarmMe System SHALL test basic CRUD operations (Create, Read, Update, Delete) on the Supabase database
4. THE FarmMe System SHALL compare data samples between local and Supabase databases to ensure consistency
5. WHEN verification completes, THE FarmMe System SHALL generate a migration report showing success or failure status for each table
