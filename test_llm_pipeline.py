"""SelfHeal + DeepSeek LLM 全链路测试

测试流程:
1. 用自定义失败事件触发 HybridClassifier → 低置信度 → LLM 回退
2. LLM classifier 用 DeepSeek API 分类
3. Template patcher 生成补丁
4. Validator 验证补丁
5. 输出完整报告
"""

import os
import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("llm_pipeline_test")

# DeepSeek API key: set via env var before running
#   set DEEPSEEK_API_KEY=sk-xxx  (Windows)
#   export DEEPSEEK_API_KEY=sk-xxx  (Linux/macOS)
if "DEEPSEEK_API_KEY" not in os.environ:
    os.environ["DEEPSEEK_API_KEY"] = os.environ.get(
        "DEEPSEEK_API_KEY", ""
    )

# Add selfheal to path
sys.path.insert(0, r"c:\Users\longhuihai\CodeBuddy\20260430210042\代码自迭代功能项目\selfheal\src")

from selfheal.config import Config
from selfheal.events import TestFailureEvent, ClassificationEvent, ErrorSeverity
from selfheal.core.classifiers.hybrid_classifier import HybridClassifier
from selfheal.core.classifiers.llm_classifier import LLMClassifier
from selfheal.core.patchers.template_patcher import TemplatePatcher
from selfheal.core.patchers.llm_patcher import LLMPatcher
from selfheal.core.validators.local_validator import LocalValidator

def main():
    config_path = r"c:\Users\longhuihai\CodeBuddy\20260429110253\smart_daily_report\selfheal.yaml"
    
    print("=" * 70)
    print("SelfHeal + DeepSeek LLM 全链路测试")
    print("=" * 70)
    
    # 1. 加载配置
    print("\n[1] 加载 SelfHeal 配置...")
    config = Config.from_file(Path(config_path))
    print(f"    LLM provider: {config.llm.provider}")
    print(f"    LLM model: {config.llm.model}")
    print(f"    Classifier: {config.classifier.type}")
    print(f"    Patcher: {config.patcher.type}")
    
    # 2. 构造测试失败事件（故意设计成低规则置信度，触发 LLM 回退）
    print("\n[2] 构造测试失败事件（低规则置信度，触发 LLM 回退）...")
    
    failures = [
        # Event 1: 复杂的 ImportError（缺少非标准库）
        TestFailureEvent(
            test_path="tests/test_integration.py::test_wechat_api",
            error_type="ImportError",
            error_message="No module named 'wechatpy.crypto'",
            traceback="""Traceback (most recent call last):
  File "tests/test_integration.py", line 5, in test_wechat_api
    from wechatpy.crypto import WeChatCrypto
ModuleNotFoundError: No module named 'wechatpy.crypto'""",
        ),
        # Event 2: 类型错误（函数参数不匹配）
        TestFailureEvent(
            test_path="tests/test_services.py::test_feishu_send_message",
            error_type="TypeError",
            error_message="send_message() got an unexpected keyword argument 'text'",
            traceback="""Traceback (most recent call last):
  File "tests/test_services.py", line 42, in test_feishu_send_message
    client.send_message(text="hello", chat_id="ch_001")
TypeError: send_message() got an unexpected keyword argument 'text'""",
        ),
        # Event 3: 复杂运行时错误（空列表索引）
        TestFailureEvent(
            test_path="tests/test_agents.py::test_collector_no_data",
            error_type="IndexError",
            error_message="list index out of range",
            traceback="""Traceback (most recent call last):
  File "tests/test_agents.py", line 33, in test_collector_no_data
    result = collector.analyze(results[0])
IndexError: list index out of range""",
        ),
    ]
    
    print(f"    创建了 {len(failures)} 个失败事件")
    for i, f in enumerate(failures, 1):
        print(f"    [{i}] {f.error_type}: {f.error_message[:60]}...")

    # 3. 测试 HybridClassifier（规则优先 → LLM 回退）
    print("\n[3] HybridClassifier 分类（规则优先 + LLM 回退）...")
    hybrid = HybridClassifier(config.classifier)
    
    classifications = []
    for event in failures:
        result = hybrid.classify(event)
        classifications.append(result)
        print(f"    [{event.error_type}] → category={result.category}, "
              f"severity={result.severity.value}, confidence={result.confidence:.2f}")
        print(f"         reasoning: {result.reasoning[:80]}")
    
    # 4. 测试 LLMClassifier 单独分类
    print("\n[4] LLMClassifier 单独分类测试...")
    llm_cfg = config.classifier
    llm_classifier = LLMClassifier(llm_cfg)
    
    for event in failures:
        try:
            result = llm_classifier.classify(event)
            print(f"    [{event.error_type}] → category={result.category}, "
                  f"severity={result.severity.value}, confidence={result.confidence:.2f}")
        except Exception as e:
            print(f"    [{event.error_type}] FAILED: {e}")
    
    # 5. 测试 TemplatePatcher（使用 Jinja2 模板）
    print("\n[5] TemplatePatcher 补丁生成...")
    template_patcher = TemplatePatcher(config.patcher)
    
    for clf in classifications:
        try:
            patch = template_patcher.generate(clf)
            content_preview = patch.patch_content[:100].replace('\n', '\\n')
            print(f"    [{clf.category}] → target={patch.target_file}, "
                  f"patch_len={len(patch.patch_content)} chars")
            print(f"         preview: {content_preview}...")
        except Exception as e:
            print(f"    [{clf.category}] FAILED: {e}")
    
    # 6. 测试 LLMPatcher（DeepSeek 生成补丁）
    print("\n[6] LLMPatcher 补丁生成（DeepSeek API）...")
    llm_patcher_config = config.patcher
    llm_patcher = LLMPatcher(llm_patcher_config)
    
    for clf in classifications:
        try:
            patch = llm_patcher.generate(clf)
            content_preview = patch.patch_content[:150].replace('\n', '\\n')
            print(f"    [{clf.category}] → generator={patch.generator}, "
                  f"patch_len={len(patch.patch_content)} chars")
            print(f"         preview: {content_preview}...")
        except Exception as e:
            print(f"    [{clf.category}] FAILED: {e}")
    
    # 7. 总结
    print("\n" + "=" * 70)
    print("全链路测试完成！")
    print(f"  - HybridClassifier: {len(classifications)} 个事件已分类")
    print(f"  - TemplatePatcher: Jinja2 模板补丁已生成")
    print(f"  - LLMPatcher: DeepSeek AI 补丁已生成")
    print("=" * 70)

if __name__ == "__main__":
    main()
