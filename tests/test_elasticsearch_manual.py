import allure
import pytest

@allure.epic("Elasticsearch Data Pipeline")
@allure.feature("Manual Testing")
class TestElasticsearchManual:
    
    @allure.story("Basic Elasticsearch Connectivity")
    @allure.title("TC-ES-001: Elasticsearch Service Connectivity")
    @allure.description("Check Elasticsearch and Kibana availability")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_elasticsearch_connectivity(self):
        allure.dynamic.tag("smoke")
        allure.dynamic.tag("elasticsearch")
        
        with allure.step("Check Elasticsearch health status"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-001_step1_elasticsearch_health.JPG", 
                             "Elasticsearch health status", allure.attachment_type.JPG)
            
        with allure.step("Check Elasticsearch indices list"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-001_step2_elasticsearch_indices.JPG", 
                             "Elasticsearch indices list", allure.attachment_type.JPG)
            
        with allure.step("Check Kibana availability"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-001_step3_agriculture_data_index.JPG", 
                             "Kibana availability", allure.attachment_type.JPG)
    
    @allure.story("Data Synchronization")
    @allure.title("TC-ES-002: PostgreSQL to Elasticsearch Data Synchronization")
    @allure.description("Check data sync from PostgreSQL to Elasticsearch")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_data_synchronization(self):
        allure.dynamic.tag("integration")
        allure.dynamic.tag("sync")
        
        with allure.step("Check documents count in Elasticsearch"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-002_step3_sample_data.JPG", 
                             "Documents count in ES", allure.attachment_type.JPG)
            
        with allure.step("Check sample data in Elasticsearch"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-002_step3_sample_data.JPG", 
                             "Sample data in ES", allure.attachment_type.JPG)
            
        with allure.step("Compare with PostgreSQL"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-002_step4_postgres_count.JPG", 
                             "PostgreSQL count", allure.attachment_type.JPG)

    @allure.story("Search Functionality")
    @allure.title("TC-ES-003: Elasticsearch Search and Query Testing")
    @allure.description("Check search and query functionality in Elasticsearch")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_functionality(self):
        allure.dynamic.tag("search")
        allure.dynamic.tag("queries")
        
        with allure.step("Search by contract name FEFZ25"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-003_step1_contract_search.JPG", 
                             "Contract search results", allure.attachment_type.JPG)
            
        with allure.step("Search by price range 100-200"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-003_step2_price_range_search.JPG", 
                             "Price range search results", allure.attachment_type.JPG)
            
        with allure.step("Show volume trend over time"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-003_step3_volume_trend.JPG", 
                             "Volume trend area chart", allure.attachment_type.JPG)
            
        with allure.step("Search Russian text"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-003_step4_russian_text_search.JPG", 
                             "Russian text search results", allure.attachment_type.JPG)

    @allure.story("Service Recovery")
    @allure.title("TC-ES-004: Elasticsearch Service Recovery")
    @allure.description("Check Elasticsearch recovery after restart")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_elasticsearch_recovery(self):
        allure.dynamic.tag("recovery")
        allure.dynamic.tag("restart")
        
        with allure.step("Stop Elasticsearch container"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-004_step1_elasticsearch_stopped.JPG", 
                             "Elasticsearch stopped", allure.attachment_type.JPG)
            
        with allure.step("Check Kibana connection errors"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-004_step2_kibana_errors.JPG", 
                             "Kibana connection errors", allure.attachment_type.JPG)
            
        with allure.step("Start Elasticsearch container"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-004_step3_elasticsearch_started.JPG", 
                             "Elasticsearch started", allure.attachment_type.JPG)
            
        with allure.step("Check recovery status"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-004_step5_kibana_recovery.JPG", 
                             "Recovery status", allure.attachment_type.JPG)
            
        with allure.step("Check data integrity after recovery"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-004_step6_data_integrity.JPG", 
                             "Data integrity after recovery", allure.attachment_type.JPG)

    @allure.story("Field Mapping")
    @allure.title("TC-ES-005: Elasticsearch Field Mapping Validation")
    @allure.description("Check field mapping in Elasticsearch index")
    @allure.severity(allure.severity_level.NORMAL)
    def test_field_mapping_validation(self):
        allure.dynamic.tag("mapping")
        allure.dynamic.tag("validation")
        
        with allure.step("Get index mapping"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-005_step1_index_mapping.JPG", 
                             "Index mapping", allure.attachment_type.JPG)
            
        with allure.step("Validate field types"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-005_step2_field_types.JPG", 
                             "Field types validation", allure.attachment_type.JPG)
            
        with allure.step("Test Russian text support"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-005_step3_russian_support.JPG", 
                             "Russian text support", allure.attachment_type.JPG)
            
        with allure.step("Test numeric aggregations"):
            allure.attach.file("quality-assurance/screenshots/elasticsearch_tests/TC-ES-005_step4_numeric_aggregations.JPG", 
                             "Numeric aggregations", allure.attachment_type.JPG)