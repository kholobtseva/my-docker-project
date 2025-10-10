import allure
import pytest
import os

@allure.epic("PostgreSQL Database")
@allure.feature("Manual Testing")
class TestPostgreSQLManual:
    
    @allure.story("Database Connectivity")
    @allure.title("TC-DB-001: PostgreSQL Service Connectivity")
    @allure.description("Check PostgreSQL database availability and basic information")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_postgresql_connectivity(self):
        allure.dynamic.tag("smoke")
        allure.dynamic.tag("postgresql")
        allure.dynamic.tag("connectivity")
        
        with allure.step("Check PostgreSQL availability"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-001_step1_postgres_availability.JPG", 
                             "PostgreSQL availability check", allure.attachment_type.JPG)
            
        with allure.step("Check database table list"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-001_step2_table_list.JPG", 
                             "Database table list", allure.attachment_type.JPG)
            
        with allure.step("Check main tables structure"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-001_step3_main_tables.JPG", 
                             "Main tables structure", allure.attachment_type.JPG)
            
        with allure.step("Check record count in tables"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-001_step4_record_count.JPG", 
                             "Record count in tables", allure.attachment_type.JPG)
    
    @allure.story("Data Integrity")
    @allure.title("TC-DB-002: Data Integrity and Constraints Validation")
    @allure.description("Validate database constraints and data integrity")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_data_integrity(self):
        allure.dynamic.tag("integrity")
        allure.dynamic.tag("constraints")
        allure.dynamic.tag("validation")
        
        with allure.step("Check unique constraints"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-002_step1_unique_constraint.JPG", 
                             "Unique constraint validation", allure.attachment_type.JPG)
            
        with allure.step("Verify primary key constraints"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-002_step2_primary_key.JPG", 
                             "Primary key validation", allure.attachment_type.JPG)
            
        with allure.step("Check NULL constraints"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-002_step3_null_check.JPG", 
                             "NULL constraint check", allure.attachment_type.JPG)

    @allure.story("CRUD Operations")
    @allure.title("TC-DB-003: CRUD Operations Testing")
    @allure.description("Test Create, Read, Update, Delete operations")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_crud_operations(self):
        allure.dynamic.tag("crud")
        allure.dynamic.tag("operations")
        allure.dynamic.tag("dml")
        
        with allure.step("Select record operation"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-003_step1_select_record.JPG", 
                             "SELECT operation test", allure.attachment_type.JPG)
            
        with allure.step("Test insert with conflict"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-003_step2_insert_conflict.JPG", 
                             "INSERT conflict test", allure.attachment_type.JPG)
            
        with allure.step("Verify update operation"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-003_step3_verify_update.JPG", 
                             "UPDATE operation verification", allure.attachment_type.JPG)

    @allure.story("Data Synchronization")
    @allure.title("TC-DB-004: Data Synchronization Health Check")
    @allure.description("Check data synchronization health and recovery")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_data_synchronization_health(self):
        allure.dynamic.tag("sync")
        allure.dynamic.tag("health")
        allure.dynamic.tag("recovery")
        
        with allure.step("Check current synchronization health"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-004_step1_current_health.JPG", 
                             "Current sync health status", allure.attachment_type.JPG)
            
        with allure.step("Update health status"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-004_step2_update_health.JPG", 
                             "Health status update", allure.attachment_type.JPG)
            
        with allure.step("Verify health update"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-004_step3_verify_health.JPG", 
                             "Health update verification", allure.attachment_type.JPG)
            
        with allure.step("Update agriculture data"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-004_step4_update_agriculture.JPG", 
                             "Agriculture data update", allure.attachment_type.JPG)
            
        with allure.step("Restore original values"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-004_step5_restore_values.JPG", 
                             "Data restoration", allure.attachment_type.JPG)

    @allure.story("Query Performance")
    @allure.title("TC-DB-005: Basic Query Performance")
    @allure.description("Test basic query performance and execution")
    @allure.severity(allure.severity_level.NORMAL)
    def test_basic_query_performance(self):
        allure.dynamic.tag("performance")
        allure.dynamic.tag("queries")
        allure.dynamic.tag("basic")
        
        with allure.step("Execute basic query"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-005_step1_basic_query.JPG", 
                             "Basic query execution", allure.attachment_type.JPG)
            
        with allure.step("Test JOIN query"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-005_step2_join_query.JPG", 
                             "JOIN query test", allure.attachment_type.JPG)
            
        with allure.step("Check query performance"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-005_step3_performance_check.JPG", 
                             "Query performance check", allure.attachment_type.JPG)

    @allure.story("Advanced Queries")
    @allure.title("TC-DB-006: Advanced Query Operations")
    @allure.description("Test complex queries and aggregations")
    @allure.severity(allure.severity_level.NORMAL)
    def test_advanced_queries(self):
        allure.dynamic.tag("advanced")
        allure.dynamic.tag("aggregations")
        allure.dynamic.tag("complex")
        
        with allure.step("Execute complex JOIN query"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-006_step1_join_query.JPG", 
                             "Complex JOIN query", allure.attachment_type.JPG)
            
        with allure.step("Test aggregation query"):
            allure.attach.file("quality-assurance/screenshots/database_tests/TC-DB-006_step2_aggregation_query.JPG", 
                             "Aggregation query test", allure.attachment_type.JPG)