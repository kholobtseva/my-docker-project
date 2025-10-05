import allure
import pytest

@allure.epic("Kafka Data Pipeline")
@allure.feature("Manual Testing")
class TestKafkaManual:
    
    @allure.story("Basic Kafka Connectivity")
    @allure.title("TC-KAFKA-001: Basic Kafka Connectivity")
    @allure.description("Check Kafka broker and topics availability")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_kafka_connectivity(self):
        allure.dynamic.tag("smoke")
        allure.dynamic.tag("kafka")
        
        with allure.step("Check container status"):
            with open("quality-assurance/test_results/TC-KAFKA-004_step1_all_containers_status.txt", "r", encoding='utf-16') as f:
                container_log = f.read()
            allure.attach(container_log, "Docker containers status", allure.attachment_type.TEXT)
            
        with allure.step("Check topics list"):
            allure.attach("kafka-topics --list", "market-data topic exists")
            
        with allure.step("Check Kafdrop availability"):
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-001_step3_kafdrop_interface.jpg", 
                             "Kafdrop interface", allure.attachment_type.JPG)
    
    @allure.story("Manual Message Producing") 
    @allure.title("TC-KAFKA-002: Manual Message Producing via AKHQ")
    @allure.description("Manual test message sending through AKHQ UI")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_manual_message_producing(self):
        allure.dynamic.tag("manual")
        allure.dynamic.tag("akhq")
        
        test_data = {
            "id_value": 999,
            "date": "2025-01-15",
            "price": 150.75, 
            "contract": "MANUAL_TEST",
            "name_rus": "Manual QA Test",
            "source": "manual_test"
        }
        
        with allure.step("Open AKHQ in browser"):
            allure.attach("http://localhost:8080", "AKHQ interface opens")
            
        with allure.step("Navigate to market-data topic"):
            allure.attach("Navigation", "Topic page displays partition info")
            
        with allure.step("Click 'Produce to topic'"):
            allure.attach("Send form", "Message sending form opens")
            
        with allure.step("Enter test message and send"):
            allure.attach("test_data", str(test_data), allure.attachment_type.JSON)
            allure.attach("Result", "Message sent successfully, confirmation appears")
            
    @allure.story("Consumer Data Processing") 
    @allure.title("TC-KAFKA-003: Consumer Data Processing and CSV Export")
    @allure.description("Check message processing by consumer and CSV export")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_consumer_data_processing(self):
        allure.dynamic.tag("integration")
        allure.dynamic.tag("consumer")
        
        with allure.step("Send test message via AKHQ"):
            test_data = {"id_value":999,"date":"2025-10-04","price":150.75,"contract":"MANUAL_TEST"}
            allure.attach(str(test_data), "Test message", allure.attachment_type.JSON)
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-003_step1_message_in_topic.jpg", 
                             "Message in Kafka topic", allure.attachment_type.JPG)
            
        with allure.step("Check consumer logs"):
            with open("quality-assurance/test_results/TC-KAFKA-003_step2_consumer_logs.txt", "r", encoding='utf-16') as f:
                consumer_log = f.read()
            allure.attach(consumer_log, "Consumer processing logs", allure.attachment_type.TEXT)
            
        with allure.step("Check CSV file creation"):
            with open("quality-assurance/test_results/TC-KAFKA-003_step3_csv_file_check.txt", "r", encoding='utf-16') as f:
                csv_check = f.read()
            allure.attach(csv_check, "CSV file check", allure.attachment_type.TEXT)
            
        with allure.step("Verify CSV data content"):
            with open("quality-assurance/test_results/TC-KAFKA-003_step5_data_normalization.txt", "r", encoding='utf-16') as f:
                csv_content = f.read()
            allure.attach(csv_content, "CSV data normalization", allure.attachment_type.TEXT)
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-003_step4_csv_content.jpg", 
                             "CSV file content", allure.attachment_type.JPG)
            
    @allure.story("Service Recovery")
    @allure.title("TC-KAFKA-004: Kafka Service Recovery After Restart")
    @allure.description("Check pipeline recovery after Kafka restart")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_kafka_recovery(self):
        allure.dynamic.tag("recovery")
        allure.dynamic.tag("restart")
        
        with allure.step("Stop Kafka broker"):
            with open("quality-assurance/test_results/TC-KAFKA-004_step1_all_containers_status.txt", "r", encoding='utf-16') as f:
                container_status = f.read()
            allure.attach(container_status, "Container status after stop", allure.attachment_type.TEXT)
            
        with allure.step("Check producer connection errors"):
            with open("quality-assurance/test_results/TC-KAFKA-004_step2_python_script_logs.txt", "r", encoding='utf-16') as f:
                error_logs = f.read()
            allure.attach(error_logs, "Producer connection errors", allure.attachment_type.TEXT)
            
        with allure.step("Start Kafka broker"):
            with open("quality-assurance/test_results/TC-KAFKA-004_step5_kafka_started.txt", "r", encoding='utf-16') as f:
                kafka_start = f.read()
            allure.attach(kafka_start, "Kafka startup status", allure.attachment_type.TEXT)
            
        with allure.step("Verify message processing recovery"):
            with open("quality-assurance/test_results/TC-KAFKA-004_step8_consumer_processing.txt", "r", encoding='utf-16') as f:
                recovery_logs = f.read()
            allure.attach(recovery_logs, "Consumer recovery logs", allure.attachment_type.TEXT)
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-004_step7_message_sent.jpg", 
                             "Message sent after recovery", allure.attachment_type.JPG)

    @allure.story("Message Validation")
    @allure.title("TC-KAFKA-005: Valid Message Processing")
    @allure.description("Check processing of correctly formatted messages")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_valid_message_processing(self):
        allure.dynamic.tag("validation")
        allure.dynamic.tag("positive")
        
        with allure.step("Send valid message via AKHQ"):
            valid_data = {"id_value":200,"date":"2025-10-04","price":106.25,"contract":"FEFZ25"}
            allure.attach(str(valid_data), "Valid test message", allure.attachment_type.JSON)
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-005_step1_message_sent.jpg", 
                             "Message sent via AKHQ", allure.attachment_type.JPG)
            
        with allure.step("Check consumer processing"):
            with open("quality-assurance/test_results/TC-KAFKA-005_step2_consumer_logs.txt", "r", encoding='utf-16') as f:
                consumer_log = f.read()
            allure.attach(consumer_log, "Consumer processing log", allure.attachment_type.TEXT)
            
        with allure.step("Verify CSV data export"):
            with open("quality-assurance/test_results/TC-KAFKA-005_step3_csv_content.txt", "r", encoding='utf-16') as f:
                csv_content = f.read()
            allure.attach(csv_content, "CSV content", allure.attachment_type.TEXT)
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-005_step3_csv_content.jpg", 
                             "CSV file content", allure.attachment_type.JPG)
                             
    @allure.story("Data Validation")
    @allure.title("TC-KAFKA-006: Invalid Date Format Handling")
    @allure.description("Check validation of incorrect date format")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_invalid_date_format(self):
        allure.dynamic.tag("validation")
        allure.dynamic.tag("negative")
        
        with allure.step("Send message with invalid date"):
            invalid_data = {"id_value":201,"date":"invalid-date","price":106.25,"contract":"FEFZ25"}
            allure.attach(str(invalid_data), "Invalid date message", allure.attachment_type.JSON)
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-006_step1_message_sent.jpg", 
                             "Message sent with invalid date", allure.attachment_type.JPG)
            
        with allure.step("Check consumer validation warnings"):
            with open("quality-assurance/test_results/TC-KAFKA-006_step2_consumer_logs.txt", "r", encoding='utf-16') as f:
                validation_logs = f.read()
            allure.attach(validation_logs, "Date validation warnings", allure.attachment_type.TEXT)

    @allure.story("Data Validation")
    @allure.title("TC-KAFKA-007: Required Field Validation")
    @allure.description("Check validation of required fields")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_required_field_validation(self):
        allure.dynamic.tag("validation")
        allure.dynamic.tag("negative")
        
        with allure.step("Send message without required 'price' field"):
            incomplete_data = {"id_value":202,"date":"2025-10-04","contract":"FEFZ25"}
            allure.attach(str(incomplete_data), "Missing required field", allure.attachment_type.JSON)
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-007_step1_message_sent.jpg", 
                             "Message without price field", allure.attachment_type.JPG)
            
        with allure.step("Check consumer validation errors"):
            with open("quality-assurance/test_results/TC-KAFKA-007_step2_consumer_logs.txt", "r", encoding='utf-16') as f:
                validation_logs = f.read()
            allure.attach(validation_logs, "Required field validation errors", allure.attachment_type.TEXT)

    @allure.story("Error Handling")
    @allure.title("TC-KAFKA-008: Invalid JSON Handling")
    @allure.description("Check handling of invalid JSON format")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_invalid_json_handling(self):
        allure.dynamic.tag("error_handling")
        allure.dynamic.tag("negative")
        
        with allure.step("Send message with invalid JSON"):
            invalid_json = '{"id_value":203,"date":"2025-10-04","price":106.25,"contract":"FEFZ25","name_rus":"Iron Ore 62% Fe","source":"moex_sgx"'
            allure.attach(invalid_json, "Invalid JSON message", allure.attachment_type.TEXT)
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-008_step1_message_sent.jpg", 
                             "Invalid JSON sent", allure.attachment_type.JPG)
            
        with allure.step("Check consumer JSON parsing errors"):
            with open("quality-assurance/test_results/TC-KAFKA-008_step2_consumer_logs.txt", "r", encoding='utf-16') as f:
                parsing_logs = f.read()
            allure.attach(parsing_logs, "JSON parsing errors", allure.attachment_type.TEXT)

    @allure.story("Error Handling")
    @allure.title("TC-KAFKA-009: Empty Message Handling")
    @allure.description("Check handling of empty messages")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_message_handling(self):
        allure.dynamic.tag("error_handling")
        allure.dynamic.tag("negative")
        
        with allure.step("Send empty message"):
            empty_data = {}
            allure.attach(str(empty_data), "Empty message", allure.attachment_type.JSON)
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-009_step1_message_sent.jpg", 
                             "Empty message sent", allure.attachment_type.JPG)
            
        with allure.step("Check consumer empty message handling"):
            with open("quality-assurance/test_results/TC-KAFKA-009_step2_consumer_logs.txt", "r", encoding='utf-16') as f:
                empty_handling_logs = f.read()
            allure.attach(empty_handling_logs, "Empty message handling", allure.attachment_type.TEXT)

    @allure.story("Performance")
    @allure.title("TC-KAFKA-010: Large Message Handling")
    @allure.description("Check handling of large volume messages")
    @allure.severity(allure.severity_level.MINOR)
    def test_large_message_handling(self):
        allure.dynamic.tag("performance")
        allure.dynamic.tag("large_data")
        
        with allure.step("Send large message"):
            large_data = {"id_value":204,"date":"2025-10-04","price":106.25,"contract":"FEFZ25","name_rus":"Iron Ore 62% Fe - large volume data test","source":"moex_sgx","extra_field":"additional_field_with_long_value"}
            allure.attach(str(large_data), "Large message", allure.attachment_type.JSON)
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-010_step1_message_sent.jpg", 
                             "Large message sent", allure.attachment_type.JPG)
            
        with allure.step("Check large message processing"):
            with open("quality-assurance/test_results/TC-KAFKA-010_step2_consumer_logs.txt", "r", encoding='utf-16') as f:
                large_msg_logs = f.read()
            allure.attach(large_msg_logs, "Large message processing", allure.attachment_type.TEXT)

    @allure.story("Security")
    @allure.title("TC-KAFKA-011: Security Data Handling")
    @allure.description("Check handling of potentially dangerous data")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_security_data_handling(self):
        allure.dynamic.tag("security")
        allure.dynamic.tag("sanitization")
        
        with allure.step("Send message with dangerous data"):
            dangerous_data = {"id_value":205,"date":"2025-10-04; DROP TABLE agriculture_moex; --","price":106.25,"contract":"FEFZ25","name_rus":"<script>alert('xss')</script>","source":"moex_sgx"}
            allure.attach(str(dangerous_data), "Dangerous data message", allure.attachment_type.JSON)
            allure.attach.file("quality-assurance/screenshots/kafka_pipeline/TC-KAFKA-011_step1_message_sent.jpg", 
                             "Dangerous data sent", allure.attachment_type.JPG)
            
        with allure.step("Check data sanitization in CSV"):
            with open("quality-assurance/test_results/TC-KAFKA-011_step2_csv_content.txt", "r", encoding='utf-16') as f:
                sanitized_csv = f.read()
            allure.attach(sanitized_csv, "Sanitized CSV data", allure.attachment_type.TEXT)