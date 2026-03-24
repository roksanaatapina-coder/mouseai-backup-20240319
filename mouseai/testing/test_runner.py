#!/usr/bin/env python3
"""
Test Runner - Запуск тестов системы
"""

import unittest
import sys
import os
import logging
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
import json

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mouseai.utils import MouseAILogger

class TestResult:
    """Результат теста"""
    
    def __init__(self, test_name: str, test_class: str):
        self.test_name = test_name
        self.test_class = test_class
        self.status = 'pending'  # pending, running, passed, failed, skipped
        self.duration = 0.0
        self.error_message = ''
        self.start_time = None
        self.end_time = None
        self.assertions = []
        
    def start(self):
        """Начать выполнение теста"""
        self.status = 'running'
        self.start_time = datetime.now()
        
    def finish(self, status: str, error_message: str = ''):
        """Завершить выполнение теста"""
        self.status = status
        self.end_time = datetime.now()
        self.error_message = error_message
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
            
    def add_assertion(self, assertion: Dict):
        """Добавить результат ассерта"""
        self.assertions.append(assertion)

class TestSuite:
    """Тестовый набор"""
    
    def __init__(self, name: str):
        self.name = name
        self.tests = []
        self.start_time = None
        self.end_time = None
        self.total_duration = 0.0
        
    def add_test(self, test_result: TestResult):
        """Добавить результат теста"""
        self.tests.append(test_result)
        
    def get_stats(self) -> Dict:
        """Получить статистику по тестам"""
        total = len(self.tests)
        passed = len([t for t in self.tests if t.status == 'passed'])
        failed = len([t for t in self.tests if t.status == 'failed'])
        skipped = len([t for t in self.tests if t.status == 'skipped'])
        running = len([t for t in self.tests if t.status == 'running'])
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'running': running,
            'success_rate': (passed / total * 100) if total > 0 else 0
        }
        
    def get_duration(self) -> float:
        """Получить общую длительность выполнения"""
        return sum(t.duration for t in self.tests)

class TestRunner:
    """Запускатель тестов"""
    
    def __init__(self):
        self.logger = MouseAILogger()
        self.suites = []
        self.current_suite = None
        self.test_results = []
        
        # Коллбэки
        self.on_test_start = None
        self.on_test_end = None
        self.on_suite_start = None
        self.on_suite_end = None
        self.on_test_progress = None
        
    def run_test_suite(self, test_class, suite_name: str = None) -> TestSuite:
        """Запустить тестовый набор"""
        if suite_name is None:
            suite_name = test_class.__name__
            
        self.current_suite = TestSuite(suite_name)
        
        if self.on_suite_start:
            self.on_suite_start(suite_name)
            
        # Создаем тестовый раннер
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(test_class)
        
        # Запускаем тесты
        runner = unittest.TextTestRunner(
            stream=sys.stdout,
            verbosity=2,
            resultclass=CustomTestResult
        )
        
        # Настраиваем коллбэки
        runner.on_test_start = self._on_test_start
        runner.on_test_end = self._on_test_end
        runner.on_test_progress = self._on_test_progress
        
        result = runner.run(suite)
        
        # Сохраняем результаты
        self.current_suite.tests = result.test_results
        self.suites.append(self.current_suite)
        
        if self.on_suite_end:
            self.on_suite_end(suite_name, self.current_suite.get_stats())
            
        return self.current_suite
        
    def run_discovery(self, start_dir: str = '.', pattern: str = 'test*.py') -> List[TestSuite]:
        """Запустить discovery тестов"""
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir, pattern=pattern)
        
        runner = unittest.TextTestRunner(
            stream=sys.stdout,
            verbosity=2,
            resultclass=CustomTestResult
        )
        
        result = runner.run(suite)
        return result.test_suites
        
    def run_specific_tests(self, test_names: List[str]) -> List[TestSuite]:
        """Запустить конкретные тесты"""
        suite = unittest.TestSuite()
        
        for test_name in test_names:
            try:
                test = unittest.defaultTestLoader.loadTestsFromName(test_name)
                suite.addTest(test)
            except Exception as e:
                self.logger.error(f"Не удалось загрузить тест {test_name}: {e}")
                
        runner = unittest.TextTestRunner(
            stream=sys.stdout,
            verbosity=2,
            resultclass=CustomTestResult
        )
        
        result = runner.run(suite)
        return result.test_suites
        
    def get_all_results(self) -> List[TestSuite]:
        """Получить все результаты тестов"""
        return self.suites
        
    def get_overall_stats(self) -> Dict:
        """Получить общую статистику"""
        total_tests = sum(len(suite.tests) for suite in self.suites)
        total_passed = sum(len([t for t in suite.tests if t.status == 'passed']) for suite in self.suites)
        total_failed = sum(len([t for t in suite.tests if t.status == 'failed']) for suite in self.suites)
        total_skipped = sum(len([t for t in suite.tests if t.status == 'skipped']) for suite in self.suites)
        total_duration = sum(suite.get_duration() for suite in self.suites)
        
        return {
            'total_suites': len(self.suites),
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_skipped': total_skipped,
            'total_duration': total_duration,
            'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
        }
        
    def export_results(self, filename: str, format: str = 'json'):
        """Экспортировать результаты тестов"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'suites': [
                {
                    'name': suite.name,
                    'tests': [
                        {
                            'name': test.test_name,
                            'class': test.test_class,
                            'status': test.status,
                            'duration': test.duration,
                            'error_message': test.error_message,
                            'assertions': test.assertions
                        }
                        for test in suite.tests
                    ],
                    'duration': suite.get_duration(),
                    'stats': suite.get_stats()
                }
                for suite in self.suites
            ],
            'overall_stats': self.get_overall_stats()
        }
        
        try:
            if format == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == 'xml':
                self._export_xml(data, filename)
            elif format == 'html':
                self._export_html(data, filename)
                
            self.logger.info(f"Результаты тестов экспортированы в {filename}")
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта результатов: {e}")
            
    def _on_test_start(self, test_name: str, test_class: str):
        """Обработчик начала теста"""
        if self.on_test_start:
            self.on_test_start(test_name, test_class)
            
    def _on_test_end(self, test_name: str, test_class: str, status: str, error_message: str = ''):
        """Обработчик окончания теста"""
        if self.on_test_end:
            self.on_test_end(test_name, test_class, status, error_message)
            
    def _on_test_progress(self, progress: float):
        """Обработчик прогресса"""
        if self.on_test_progress:
            self.on_test_progress(progress)
            
    def _export_xml(self, data: Dict, filename: str):
        """Экспортировать в XML формат"""
        import xml.etree.ElementTree as ET
        
        root = ET.Element('testsuites')
        
        for suite_data in data['suites']:
            suite_elem = ET.SubElement(root, 'testsuite', name=suite_data['name'])
            
            for test_data in suite_data['tests']:
                test_elem = ET.SubElement(suite_elem, 'testcase', name=test_data['name'])
                
                if test_data['status'] == 'failed':
                    failure = ET.SubElement(test_elem, 'failure')
                    failure.text = test_data['error_message']
                elif test_data['status'] == 'skipped':
                    skipped = ET.SubElement(test_elem, 'skipped')
                    
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        
    def _export_html(self, data: Dict, filename: str):
        """Экспортировать в HTML формат"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 20px; }}
        .stat {{ background: white; padding: 10px; border-radius: 5px; }}
        .suite {{ margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; }}
        .test {{ margin-left: 20px; padding: 5px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .skipped {{ color: orange; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Results</h1>
        <div class="stats">
            <div class="stat">Suites: {data['overall_stats']['total_suites']}</div>
            <div class="stat">Tests: {data['overall_stats']['total_tests']}</div>
            <div class="stat">Passed: {data['overall_stats']['total_passed']}</div>
            <div class="stat">Failed: {data['overall_stats']['total_failed']}</div>
            <div class="stat">Skipped: {data['overall_stats']['total_skipped']}</div>
            <div class="stat">Success Rate: {data['overall_stats']['success_rate']:.1f}%</div>
        </div>
    </div>
"""
        
        for suite_data in data['suites']:
            html += f"""
    <div class="suite">
        <h2>{suite_data['name']} ({suite_data['stats']['total']} tests)</h2>
"""
            
            for test_data in suite_data['tests']:
                status_class = test_data['status']
                html += f"""
        <div class="test {status_class}">
            <span class="{status_class}">[{test_data['status']}]</span>
            {test_data['name']} ({test_data['duration']:.3f}s)
            {f'<br><small>{test_data['error_message']}</small>' if test_data['error_message'] else ''}
        </div>
"""
                
            html += "</div>"
            
        html += "</body></html>"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

class CustomTestResult(unittest.TestResult):
    """Кастомный результат теста"""
    
    def __init__(self):
        super().__init__()
        self.test_results = []
        self.test_suites = []
        self.current_test = None
        
    def startTest(self, test):
        """Начало теста"""
        super().startTest(test)
        
        test_name = test._testMethodName
        test_class = test.__class__.__name__
        
        self.current_test = TestResult(test_name, test_class)
        self.current_test.start()
        
        if hasattr(self, 'on_test_start') and self.on_test_start:
            self.on_test_start(test_name, test_class)
            
    def addSuccess(self, test):
        """Успешный тест"""
        super().addSuccess(test)
        
        if self.current_test:
            self.current_test.finish('passed')
            self.test_results.append(self.current_test)
            
        if hasattr(self, 'on_test_end') and self.on_test_end:
            self.on_test_end(test._testMethodName, test.__class__.__name__, 'passed')
            
    def addError(self, test, err):
        """Ошибка в тесте"""
        super().addError(test, err)
        
        if self.current_test:
            self.current_test.finish('failed', str(err[1]))
            self.test_results.append(self.current_test)
            
        if hasattr(self, 'on_test_end') and self.on_test_end:
            self.on_test_end(test._testMethodName, test.__class__.__name__, 'failed', str(err[1]))
            
    def addFailure(self, test, err):
        """Проваленный тест"""
        super().addFailure(test, err)
        
        if self.current_test:
            self.current_test.finish('failed', str(err[1]))
            self.test_results.append(self.current_test)
            
        if hasattr(self, 'on_test_end') and self.on_test_end:
            self.on_test_end(test._testMethodName, test.__class__.__name__, 'failed', str(err[1]))
            
    def addSkip(self, test, reason):
        """Пропущенный тест"""
        super().addSkip(test, reason)
        
        if self.current_test:
            self.current_test.finish('skipped', reason)
            self.test_results.append(self.current_test)
            
        if hasattr(self, 'on_test_end') and self.on_test_end:
            self.on_test_end(test._testMethodName, test.__class__.__name__, 'skipped', reason)

def create_test_runner() -> TestRunner:
    """Создать запускатель тестов"""
    return TestRunner()