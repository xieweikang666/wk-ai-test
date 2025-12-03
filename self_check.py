#!/usr/bin/env python3
"""
自测脚本 - 评估AI分析回答质量
用于代码调整后自动验证分析质量
"""
import asyncio
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from agent.simple_planner import get_planner
from agent.functions import get_executor
from agent.analyzer import analyze_result

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """测试用例"""
    id: str
    question: str
    expected_keywords: List[str]  # 预期包含的关键词
    expected_focus: str  # 预期分析重点
    description: str  # 测试用例描述
    min_length: int = 100  # 最小回答长度


@dataclass
class TestResult:
    """测试结果"""
    test_id: str
    question: str
    answer: str
    sql: str
    passed: bool
    score: float  # 0-100分
    issues: List[str]
    execution_time: float


class AnswerQualityChecker:
    """回答质量检查器"""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.results: List[TestResult] = []
    
    def check_relevance(self, answer: str, question: str, expected_focus: str) -> Tuple[bool, List[str]]:
        """检查回答相关性"""
        issues = []
        
        # 检查是否针对用户问题
        if "设备数量" in question and "device_count" not in answer.lower():
            if "count" in answer.lower() and "device" not in answer.lower():
                issues.append("可能分析了错误的数据列（count而非device_count）")
        
        # 检查是否包含预期的分析重点
        if expected_focus.lower() not in answer.lower():
            issues.append(f"缺少预期的分析重点：{expected_focus}")
        
        # 检查是否有空话套话
        empty_phrases = ["总的来说", "综上所述", "值得注意的是", "需要指出的是"]
        if sum(1 for phrase in empty_phrases if phrase in answer) > 2:
            issues.append("包含过多空话套话")
        
        return len(issues) == 0, issues
    
    def check_data_accuracy(self, answer: str) -> Tuple[bool, List[str]]:
        """检查数据准确性"""
        issues = []
        
        # 查找百分比数字，检查是否合理
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%|百分比'
        percentages = re.findall(percentage_pattern, answer)
        
        for pct in percentages:
            try:
                pct_float = float(pct)
                if pct_float > 100:
                    issues.append(f"异常的百分比值：{pct}%")
                elif pct_float < 0:
                    issues.append(f"负数的百分比值：{pct}%")
            except ValueError:
                continue
        
        # 检查是否有编造数据的嫌疑
        if "约" in answer and "%" in answer:
            # 简单检查：避免过多模糊表述
            vague_count = answer.count("约") + answer.count("大概") + answer.count("左右")
            if vague_count > 3:
                issues.append("模糊表述过多，可能影响数据准确性")
        
        return len(issues) == 0, issues
    
    def check_value_orientation(self, answer: str, expected_keywords: List[str]) -> Tuple[bool, List[str]]:
        """检查价值导向"""
        issues = []
        
        # 检查是否包含关键词
        found_keywords = sum(1 for keyword in expected_keywords if keyword in answer)
        if found_keywords < len(expected_keywords) / 2:
            issues.append(f"缺少预期的关键词：{expected_keywords}")
        
        # 检查是否有具体建议
        if "建议" not in answer and "优化" not in answer:
            if "问题" in answer:  # 如果提到了问题但没有建议
                issues.append("指出了问题但未提供具体建议")
        
        # 检查分析结构
        required_structures = ["发现", "数据", "分析"]
        structure_score = sum(1 for structure in required_structures if structure in answer)
        if structure_score < 2:
            issues.append("分析结构不够完整")
        
        return len(issues) == 0, issues
    
    def check_length_quality(self, answer: str, min_length: int) -> Tuple[bool, List[str]]:
        """检查长度质量"""
        issues = []
        
        if len(answer) < min_length:
            issues.append(f"回答过短（{len(answer)}字符），至少需要{min_length}字符")
        elif len(answer) > 800:
            issues.append("回答过长，可能包含冗余信息")
        
        # 检查句子完整性
        sentences = answer.split("。")
        incomplete_sentences = sum(1 for s in sentences if len(s.strip()) < 5)
        if incomplete_sentences > len(sentences) * 0.3:
            issues.append("存在过多不完整的句子")
        
        return len(issues) == 0, issues
    
    def evaluate_answer(self, test_case: TestCase, answer: str, sql: str) -> TestResult:
        """综合评估回答质量"""
        start_time = time.time()
        
        all_issues = []
        
        # 相关性检查
        relevance_ok, relevance_issues = self.check_relevance(answer, test_case.question, test_case.expected_focus)
        all_issues.extend(relevance_issues)
        
        # 数据准确性检查
        accuracy_ok, accuracy_issues = self.check_data_accuracy(answer)
        all_issues.extend(accuracy_issues)
        
        # 价值导向检查
        value_ok, value_issues = self.check_value_orientation(answer, test_case.expected_keywords)
        all_issues.extend(value_issues)
        
        # 长度质量检查
        length_ok, length_issues = self.check_length_quality(answer, test_case.min_length)
        all_issues.extend(length_issues)
        
        # 计算总分
        passed_checks = sum([relevance_ok, accuracy_ok, value_ok, length_ok])
        total_checks = 4
        base_score = (passed_checks / total_checks) * 100
        
        # 根据问题数量调整分数
        if len(all_issues) == 0:
            score = 100
        else:
            score = max(0, base_score - (len(all_issues) * 5))
        
        execution_time = time.time() - start_time
        
        result = TestResult(
            test_id=test_case.id,
            question=test_case.question,
            answer=answer,
            sql=sql,
            passed=score >= 70,  # 70分以上算通过
            score=score,
            issues=all_issues,
            execution_time=execution_time
        )
        
        if result.passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        self.results.append(result)
        return result


class SelfCheckRunner:
    """自测运行器"""
    
    def __init__(self):
        self.quality_checker = AnswerQualityChecker()
    
    def load_test_cases(self, test_file: str = "test_cases.json") -> List[TestCase]:
        """加载测试用例"""
        test_path = Path(test_file)
        
        if test_path.exists():
            with open(test_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [TestCase(**case) for case in data["test_cases"]]
        
        # 默认测试用例
        return self._get_default_test_cases()
    
    def _get_default_test_cases(self) -> List[TestCase]:
        """获取默认测试用例"""
        return [
            TestCase(
                id="test_001",
                question="查询近3h，各个运营商的探测设备数量，用table的方式输出",
                expected_keywords=["设备", "数量", "运营商", "分布"],
                expected_focus="设备数量分布",
                description="测试设备数量分析的准确性"
            ),
            TestCase(
                id="test_002", 
                question="分析浙江电信近1h的网络质量情况",
                expected_keywords=["延迟", "丢包", "网络质量", "性能"],
                expected_focus="网络质量分析",
                description="测试网络质量分析的专业性"
            ),
            TestCase(
                id="test_003",
                question="对比各个省份探测结果的覆盖率",
                expected_keywords=["覆盖", "省份", "分布", "对比"],
                expected_focus="覆盖率分析",
                description="测试地区覆盖分析的全面性"
            ),
            TestCase(
                id="test_004",
                question="查看最近探测任务中延迟最高的问题节点",
                expected_keywords=["延迟", "节点", "问题", "性能"],
                expected_focus="问题节点识别",
                description="测试问题发现和定位能力"
            ),
            TestCase(
                id="test_005",
                question="分析不同时段的网络性能变化趋势",
                expected_keywords=["时段", "趋势", "性能", "变化"],
                expected_focus="趋势分析",
                description="时间序列分析能力"
            )
        ]
    
    async def run_single_test(self, test_case: TestCase) -> TestResult:
        """运行单个测试"""
        logger.info(f"执行测试 {test_case.id}: {test_case.description}")
        logger.info(f"问题: {test_case.question}")
        
        try:
            # 1. 生成查询计划
            planner = get_planner()
            query_plan = planner.plan(test_case.question)
            
            # 2. 执行查询
            executor = get_executor()
            df = executor.run_query(query_plan)
            sql = executor.get_generated_sql(query_plan)
            
            # 3. 生成分析
            answer = executor.explain_result(df, query_plan)
            
            # 4. 评估质量
            result = self.quality_checker.evaluate_answer(test_case, answer, sql)
            
            logger.info(f"测试 {test_case.id} 完成，得分: {result.score:.1f}")
            if not result.passed:
                logger.warning(f"问题: {'; '.join(result.issues)}")
            
            return result
            
        except Exception as e:
            logger.error(f"测试 {test_case.id} 执行失败: {e}")
            return TestResult(
                test_id=test_case.id,
                question=test_case.question,
                answer=f"执行失败: {str(e)}",
                sql="",
                passed=False,
                score=0,
                issues=[f"执行异常: {str(e)}"],
                execution_time=0
            )
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("🚀 开始自测...")
        
        test_cases = self.load_test_cases()
        start_time = time.time()
        
        # 并行执行测试
        tasks = [self.run_single_test(case) for case in test_cases]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # 统计结果
        passed_count = self.quality_checker.passed_tests
        failed_count = self.quality_checker.failed_tests
        total_count = len(results)
        pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
        
        # 生成报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total_count,
                "passed": passed_count,
                "failed": failed_count,
                "pass_rate": pass_rate,
                "execution_time": total_time
            },
            "details": []
        }
        
        for result in results:
            report["details"].append({
                "test_id": result.test_id,
                "question": result.question,
                "passed": result.passed,
                "score": result.score,
                "issues": result.issues,
                "execution_time": result.execution_time,
                "answer_length": len(result.answer)
            })
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_file: str = "self_check_report.json"):
        """保存测试报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"📊 测试报告已保存到: {output_file}")
    
    def print_summary(self, report: Dict[str, Any]):
        """打印测试摘要"""
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("🧪 自测完成！")
        print("="*60)
        print(f"测试总数: {summary['total']}")
        print(f"通过数量: {summary['passed']}")
        print(f"失败数量: {summary['failed']}")
        print(f"通过率: {summary['pass_rate']:.1f}%")
        print(f"执行时间: {summary['execution_time']:.2f}秒")
        
        if summary['failed'] > 0:
            print(f"\n❌ 失败的测试:")
            for detail in report["details"]:
                if not detail["passed"]:
                    print(f"  - {detail['test_id']}: {detail['question'][:30]}...")
                    if detail["issues"]:
                        print(f"    问题: {'; '.join(detail['issues'])}")
        
        print("\n" + "="*60)


async def main():
    """主函数"""
    runner = SelfCheckRunner()
    
    try:
        # 运行所有测试
        report = await runner.run_all_tests()
        
        # 打印摘要
        runner.print_summary(report)
        
        # 保存报告
        runner.save_report(report)
        
        # 如果通过率低于70%，返回非0退出码
        if report["summary"]["pass_rate"] < 70:
            logger.warning("⚠️  自测未通过，分析质量需要改进")
            exit(1)
        else:
            logger.info("✅ 自测通过，分析质量符合要求")
            
    except Exception as e:
        logger.error(f"自测执行失败: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())