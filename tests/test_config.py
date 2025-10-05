import pytest
import os
import allure

@allure.epic("Project Configuration")
@allure.feature("Docker and Dependencies Setup")
class TestProjectConfig:

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

    @allure.story("Docker Build for Delivery")
    @allure.title("TC-CONFIG-002: Dockerfile for Hub Publication")
    @allure.description("Проверка инструкций сборки для публикации в Docker Hub")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_dockerfile_content(self):
        allure.dynamic.tag("docker")
        allure.dynamic.tag("build")
        
        with allure.step("Прочитать и проанализировать Dockerfile"):
            with open('Dockerfile', 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            allure.attach(content, "Полное содержимое Dockerfile", allure.attachment_type.TEXT)
            
        with allure.step("Проверить базовый образ Python"):
            has_python_base = any('FROM python' in line for line in lines)
            assert has_python_base, "Dockerfile должен использовать базовый образ Python"
            python_line = next(line for line in lines if 'FROM python' in line)
            allure.attach(f"✓ Базовый образ: {python_line.strip()}", "Проверка базового образа", allure.attachment_type.TEXT)
            
        with allure.step("Проверить копирование зависимостей"):
            has_requirements = any('requirements.txt' in line for line in lines)
            assert has_requirements, "Dockerfile должен копировать requirements.txt"
            allure.attach("✓ Зависимости requirements.txt включены", "Проверка зависимостей", allure.attachment_type.TEXT)
            
        with allure.step("Проверить копирование приложения"):
            has_main_py = any('app/main.py' in line for line in lines)
            assert has_main_py, "Dockerfile должен копировать app/main.py"
            allure.attach("✓ Основной скрипт app/main.py включен", "Проверка приложения", allure.attachment_type.TEXT)
            
        with allure.step("Проверить общую структуру Dockerfile"):
            copy_commands = [line for line in lines if line.strip().startswith('COPY')]
            run_commands = [line for line in lines if line.strip().startswith('RUN')]
            
            copy_info = f"COPY команд: {len(copy_commands)}\n" + "\n".join(copy_commands)
            run_info = f"RUN команд: {len(run_commands)}\n" + "\n".join(run_commands[:3])
            
            allure.attach(copy_info, "Анализ COPY команд", allure.attachment_type.TEXT)
            allure.attach(run_info, "Анализ RUN команд", allure.attachment_type.TEXT)