@allure.story("Docker Configuration")
@allure.title("TC-CONFIG-001: Core Docker Files for Delivery")
@allure.description("Проверка наличия ключевых файлов для сборки и публикации в Docker Hub")
@allure.severity(allure.severity_level.CRITICAL)
def test_required_files_exist(self):
    allure.dynamic.tag("docker")
    allure.dynamic.tag("delivery")
    
    required_files = [
        'Dockerfile',
        'docker-compose.yml', 
        'requirements.txt',
        'app/main.py'
    ]
    
    with allure.step("Определить список файлов для сборки Docker образа"):
        files_list = "\n".join([f"• {file}" for file in required_files])
        allure.attach(files_list, "Файлы для сборки и доставки в Docker Hub", allure.attachment_type.TEXT)
        
    missing_files = []
    
    with allure.step("Проверить наличие каждого файла для CD пайплайна"):
        for file in required_files:
            if os.path.exists(file):
                file_size = os.path.getsize(file)
                allure.attach(f"✓ {file} - найден ({file_size} bytes)", "Статус файла доставки", allure.attachment_type.TEXT)
            else:
                missing_files.append(file)
                allure.attach(f"✗ {file} - ОТСУТСТВУЕТ (блокирует доставку)", "Статус файла доставки", allure.attachment_type.TEXT)
                
    with allure.step("Валидация готовности к доставке в Docker Hub"):
        assert len(missing_files) == 0, f"Отсутствуют файлы для доставки: {', '.join(missing_files)}"
        allure.attach("✓ Все файлы для сборки и доставки в Docker Hub присутствуют", "Итог проверки CD", allure.attachment_type.TEXT)